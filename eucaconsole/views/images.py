# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS images

"""
import re

from beaker.cache import cache_region, cache_managers
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..constants.images import PLATFORM_CHOICES, PlatformChoice
from ..forms.images import ImageForm, ImagesFiltersForm
from ..models import Notification
from ..views import LandingPageView, TaggedItemView
from . import boto_error_handler


class ImagesView(LandingPageView):
    TEMPLATE = '../templates/images/images.pt'

    def __init__(self, request):
        super(ImagesView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/images'
        self.json_items_endpoint = self.get_json_endpoint('images_json')
        self.filters_form = ImagesFiltersForm(
            self.request, cloud_type=self.cloud_type, formdata=self.request.params or None)
        self.filter_keys = self.get_filter_keys()
        self.sort_keys = self.get_sort_keys()
        self.render_dict = dict(
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
            filter_fields=True,
            filters_form=self.filters_form,
        )

    @view_config(route_name='images', renderer=TEMPLATE)
    def images_landing(self):
        # filter_keys are passed to client-side filtering in search box
        # sort_keys are passed to sorting drop-down
        return self.render_dict

    @staticmethod
    def get_filter_keys():
        return ['architecture', 'description', 'id', 'name', 'owner_alias',
                'platform_name', 'root_device_type', 'tagged_name']

    @staticmethod
    def get_sort_keys():
        return [
            dict(key='id', name='ID'),
            dict(key='name', name=_(u'Image name: A to Z')),
            dict(key='-name', name=_(u'Image name: Z to A')),
            dict(key='architecture', name=_(u'Architecture')),
            dict(key='root_device_type', name=_(u'Root device type')),
            dict(key='platform_name', name=_(u'Platform')),
            dict(key='description', name=_(u'Description')),
        ]

    @staticmethod
    def invalidate_images_cache():
        for manager in cache_managers.values():
            if '_get_images_cache' in manager.namespace.namespace:
                manager.clear()


class ImagesJsonView(LandingPageView):
    """Images returned as JSON"""
    @view_config(route_name='images_json', renderer='json', request_method='GET')
    def images_json(self):
        images = []
        # Apply filters, skipping owner_alias since it's leveraged in self.get_items() below
        filtered_items = self.filter_items(self.get_items(), ignore=['owner_alias', 'platform'])
        if self.request.params.getall('platform'):
            filtered_items = self.filter_by_platform(filtered_items)
        for image in filtered_items:
            platform = ImageView.get_platform(image)
            images.append(dict(
                architecture=image.architecture,
                description=image.description,
                id=image.id,
                name=image.name,
                tagged_name=TaggedItemView.get_display_name(image),
                owner_alias=image.owner_alias,
                platform_name=ImageView.get_platform_name(platform),
                platform_key=ImageView.get_platform_key(platform),  # Used in image picker widget
                root_device_type=image.root_device_type,
            ))
        return dict(results=images)

    def get_items(self):
        owner_alias = self.request.params.get('owner_alias')
        if not owner_alias and self.cloud_type == 'aws':
            # Set default alias to 'amazon' for AWS
            owner_alias = 'amazon'
        owners = [owner_alias] if owner_alias else []
        conn = self.get_connection()
        region = self.request.session.get('region')
        items = self.get_images(conn, owners, [], region)
        # This is to included shared images in the owned images list per GUI-374
        if owner_alias == 'self':
            items.extend(self.get_images(conn, [], ['self'], region))
        return items

    def get_images(self, conn, owners, executors, region):
        """Get images, leveraging Beaker cache for long_term duration (3600 seconds)"""
        cache_key = 'images_cache_{owners}_{executors}_{region}'.format(
            owners=owners, executors=executors, region=region)

        # Heads up!  Update cache key if we allow filters to be passed here
        @cache_region('long_term', cache_key)
        def _get_images_cache(_owners, _executors, _region):
            with boto_error_handler(self.request):
                filters = {'image-type': 'machine'}
                return conn.get_all_images(owners=_owners, executable_by=_executors, filters=filters) if conn else []
        return _get_images_cache(owners, executors, region)

    def filter_by_platform(self, items):
        filtered_items = []
        for item in items:
            for platform in self.request.params.getall('platform'):
                if self.cloud_type == 'euca' and platform == 'linux':
                    platform = ''
                if item.platform == platform:
                    filtered_items.append(item)
        return filtered_items


class ImageView(TaggedItemView):
    """Views for single Image"""
    TEMPLATE = '../templates/images/image_view.pt'

    def __init__(self, request):
        super(ImageView, self).__init__(request)
        self.conn = self.get_connection()
        self.image = self.get_image()
        self.image_form = ImageForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.image
        self.image_display_name=self.get_display_name()
        self.render_dict = dict(
            image=self.image,
            image_display_name=self.image_display_name,
            image_form=self.image_form,
        )

    def get_image(self):
        image_param = self.request.matchdict.get('id')
        images_param = [image_param]
        images = []
        if self.conn:
            with boto_error_handler(self.request):
                images = self.conn.get_all_images(image_ids=images_param)
        image = images[0] if images else None
        if image:
            attrs = image.__dict__
            image.block_device_names = []
            if attrs['block_device_mapping'] is not None:
                for attr in attrs['block_device_mapping']:
                    image.block_device_names.append({
                        'name': attr, 'value': attrs['block_device_mapping'][attr].__dict__
                    })
            image.platform = self.get_platform(image)
            image.platform_name = ImageView.get_platform_name(image.platform)
        return image

    @view_config(route_name='image_view', renderer=TEMPLATE)
    def image_view(self):
        return self.render_dict
 
    @view_config(route_name='image_update', request_method='POST', renderer=TEMPLATE)
    def image_update(self):
        if self.image_form.validate():
            self.update_tags()

            location = self.request.route_path('image_view', id=self.image.id)
            msg = _(u'Successfully modified image')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return self.render_dict

    @staticmethod
    def get_platform(image):
        """Give me a boto.ec2.image.Image object and I'll give you the platform"""
        unknown = PlatformChoice(key='unknown', pattern=r'unknown', name='unknown')
        # Use platform if exists (e.g. 'windows')
        lookup_attrs = ['name', 'description']
        if image:
            if image.platform:
                return PlatformChoice(key=image.platform, pattern='', name=image.platform)
            # Try lookup using lookup attributes
            for lookup in lookup_attrs:
                attr_value = getattr(image, lookup, '')
                if attr_value:
                    for choice in PLATFORM_CHOICES:
                        if re.findall(choice.pattern, attr_value, re.IGNORECASE):
                            return choice
            return unknown

    def get_display_name(self):
        if self.image:
            return TaggedItemView.get_display_name(self.image)
        return None

    @staticmethod
    def get_platform_name(platform):
        """platform could be either a unicode object (e.g. 'windows')
           or a eucaconsole.constants.images.PlatformChoice object
        """
        if isinstance(platform, unicode):
            return platform
        return platform.name

    @staticmethod
    def get_platform_key(platform):
        """platform could be either a unicode object (e.g. 'windows')
           or a eucaconsole.constants.images.PlatformChoice object
        """
        if isinstance(platform, unicode):
            return platform
        return platform.key

