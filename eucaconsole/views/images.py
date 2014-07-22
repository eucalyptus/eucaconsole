# -*- coding: utf-8 -*-
# Copyright 2013-2014 Eucalyptus Systems, Inc.
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Pyramid views for Eucalyptus and AWS images

"""
import re

import logging

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
import pylibmc

from ..constants.images import PLATFORM_CHOICES, PlatformChoice
from ..forms.images import ImageForm, ImagesFiltersForm, DeregisterImageForm
from ..i18n import _
from ..models import Notification
from ..models.auth import User
from ..views import LandingPageView, TaggedItemView, JSONResponse
from . import boto_error_handler
from ..caches import long_term
from ..caches import invalidate_cache

import panels


class ImagesView(LandingPageView):
    TEMPLATE = '../templates/images/images.pt'

    def __init__(self, request):
        super(ImagesView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/images'
        self.json_items_endpoint = self.get_json_endpoint('images_json')
        self.filters_form = ImagesFiltersForm(
            self.request, cloud_type=self.cloud_type, formdata=self.request.params or None)
        self.deregister_form = DeregisterImageForm(self.request, formdata=self.request.params or None)
        self.conn = self.get_connection()
        self.account_id = User.get_account_id(ec2_conn=self.conn, request=self.request)
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
            deregister_form=self.deregister_form,
            account_id=self.account_id,
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
    def invalidate_images_cache(request):
        region = request.session.get('region')
        acct = request.session.get('account', '')
        if acct == '':
            acct = request.session.get('access_id', '')
        invalidate_cache(long_term, 'images', None, [], [], region, acct)
        invalidate_cache(long_term, 'images', None, [u'self'], [], region, acct)
        invalidate_cache(long_term, 'images', None, [], [u'self'], region, acct)


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
                location=image.location,
                tagged_name=TaggedItemView.get_display_name(image),
                name_id=ImageView.get_image_name_id(image),
                owner_id=image.owner_id,
                owner_alias=image.owner_alias,
                platform_name=ImageView.get_platform_name(platform),
                platform_key=ImageView.get_platform_key(platform),  # Used in image picker widget
                root_device_type=image.root_device_type,
                snapshot_id=ImageView.get_image_snapshot_id(image),
            ))
        return dict(results=images)

    @view_config(route_name='image_json', renderer='json', request_method='GET')
    def image_json(self):
        image_id = self.request.matchdict.get('id')
        with boto_error_handler(self.request):
            conn = self.get_connection()
            image = conn.get_image(image_id)
            if image is None:
                return JSONResponse(status=400, message="image id not valid")
            platform = ImageView.get_platform(image)
            bdm_dict = {}
            bdm_object = image.block_device_mapping
            for key, device in bdm_object.items():
                bdm_dict[key] = dict(
                    is_root=True if panels.get_root_device_name(image) == key else False,
                    volume_type=device.volume_type,
                    virtual_name=device.ephemeral_name,
                    snapshot_id=device.snapshot_id,
                    size=device.size,
                    delete_on_termination=device.delete_on_termination,
                )
            return dict(results=(dict(
                architecture=image.architecture,
                description=image.description,
                id=image.id,
                name=image.name,
                location=image.location,
                block_device_mapping=bdm_dict,
                tagged_name=TaggedItemView.get_display_name(image),
                owner_alias=image.owner_alias,
                platform_name=ImageView.get_platform_name(platform),
                platform_key=ImageView.get_platform_key(platform),  # Used in image picker widget
                root_device_type=image.root_device_type,
            )))

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
            items.extend(self.get_images(conn, [], [u'self'], region))
        return items

    @long_term.cache_on_arguments(namespace='images')
    def _get_images_cached_(self, _owners, _executors, _ec2_region, acct):
        """
        This method is decorated and will cache the image set
        """
        return self._get_images_(_owners, _executors, _ec2_region)

    def _get_images_(self, _owners, _executors, _ec2_region):
        """
        this method produces a cachable list of images
        """
        with boto_error_handler(self.request):
            logging.info("loading images from server (not cache)")
            filters = {'image-type': 'machine'}
            images = self.get_connection().get_all_images(owners=_owners, executable_by=_executors, filters=filters)
            ret = []
            for idx, img in enumerate(images):
                # trim some un-necessary items we don't need to cache
                del img.connection
                del img.region
                del img.product_codes
                del img.billing_products
                # alter things we want to cache, but are un-picklable
                if img.block_device_mapping:
                    for bdm in img.block_device_mapping.keys():
                        mapping_type = img.block_device_mapping[bdm]
                        del mapping_type.connection
                ret.append(img)
            return ret

    def get_images(self, conn, owners, executors, ec2_region):
        """
        This method sets the right account value so we cache private images per-acct
        and handles caching error by fetching the data from the server.
        """
        acct = self.request.session.get('account', '')
        if acct == '':
            acct = self.request.session.get('access_id', '')
        if 'amazon' in owners or 'aws-marketplace' in owners:
            acct = ''
        try:
            return self._get_images_cached_(owners, executors, ec2_region, acct)
        except pylibmc.Error as err:
            logging.warn('memcached not responding')
            return self._get_images_(owners, executors, ec2_region)


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
        self.account_id = User.get_account_id(ec2_conn=self.conn, request=self.request)
        self.image = self.get_image()
        self.image_form = ImageForm(self.request, image=self.image, conn=self.conn, formdata=self.request.params or None)
        self.deregister_form = DeregisterImageForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.image
        self.image_display_name = self.get_display_name()
        self.is_public = str(self.image.is_public).lower() if self.image else False
        self.is_owned_by_user = self.check_if_image_owned_by_user()
        self.image_launch_permissions = self.get_image_launch_permissions_array()
        self.render_dict = dict(
            image=self.image,
            is_public = self.is_public,
            is_owned_by_user = self.is_owned_by_user,
            image_launch_permissions = self.image_launch_permissions,
            image_description=self.image.description if self.image else '',
            image_display_name=self.image_display_name,
            image_name_id=ImageView.get_image_name_id(self.image),
            image_form=self.image_form,
            deregister_form=self.deregister_form,
            account_id=self.account_id,
            snapshot_images_registered=self.get_images_registered_from_snapshot_count(),
        )

    def check_if_image_owned_by_user(self):
        if self.image and self.image.owner_id == self.account_id:
            return True
        return False 

    def get_image_launch_permissions_array(self):
        if self.is_owned_by_user is False: 
            return [] 
        launch_permissions = self.image.get_launch_permissions()
        if launch_permissions is None or not 'user_ids' in launch_permissions:
            return []
        lp_array = [lp.encode('ascii', 'ignore') for lp in launch_permissions['user_ids']]
        return lp_array

    def get_image(self):
        image_param = self.request.matchdict.get('id') or self.request.params.get('image_id')
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

    def get_images_registered_from_snapshot_count(self):
        if self.image and self.image.root_device_type == 'ebs':
            bdm_values = self.image.block_device_mapping.values()
            if bdm_values:
                snapshot_id = getattr(bdm_values[0], 'snapshot_id', None)
                if snapshot_id:
                    with boto_error_handler(self.request):
                        images = self.conn.get_all_images(filters={'block-device-mapping.snapshot-id': [snapshot_id]})
                        return len(images)
        return 0

    @view_config(route_name='image_view', renderer=TEMPLATE)
    def image_view(self):
        if self.image is None:
            raise HTTPNotFound()
        return self.render_dict
 
    @view_config(route_name='image_update', request_method='POST', renderer=TEMPLATE)
    def image_update(self):
        if self.image_form.validate():
            self.update_tags()

            if self.image and self.is_owned_by_user is True: 
                # Update the Image Description
                description = self.request.params.get('description', '')
                if self.image.description != description:
                    if self.cloud_type == 'aws' and description == '':
                        description = "-"
                    params = { 'ImageId': self.image.id, 'Description.Value': description }
                    with boto_error_handler(self.request):
                        self.conn.get_status('ModifyImageAttribute', params, verb='POST')

                # Update the Image to be Public
                is_public = self.request.params.get('sharing')
                current_is_public = str(self.image.is_public).lower()
                if is_public != current_is_public:
                    lp_params = {}
                    if is_public == "true":
                        lp_params = { 'ImageId': self.image.id, 'LaunchPermission.Add.1.Group': 'all' }
                    else:
                        lp_params = { 'ImageId': self.image.id, 'LaunchPermission.Remove.1.Group': 'all' }
                    with boto_error_handler(self.request):
                        self.conn.get_status('ModifyImageAttribute', lp_params, verb='POST')

                # Update the Image Launch Permissions
                lp_array = self.request.params.getall('launch-permissions-inputbox')
                self.image_update_launch_permissions(lp_array)

            # Clear images cache
            ImagesView.invalidate_images_cache(self.request)

            location = self.request.route_path('image_view', id=self.image.id)
            msg = _(u'Successfully modified image')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    def image_update_launch_permissions(self, new_launch_permissions):
        new_launch_permissions = [u.encode('ascii', 'ignore') for u in new_launch_permissions]

        self.image_add_new_launch_permissions(new_launch_permissions)
        self.image_remove_deleted_launch_permissions(new_launch_permissions)
        return 

    def image_add_new_launch_permissions(self, new_launch_permissions):
        success_msg = ''
        error_msg = ''
        for new_lp in new_launch_permissions:
            is_new = True
            for lp in self.image_launch_permissions:
                if lp == new_lp:
                    is_new = False
            if is_new:
                (msg, queue) = self.image_add_launch_permission(new_lp)
                if queue is Notification.SUCCESS:
                    success_msg += msg + " "
                else:
                    error_msg += msg + " "

        if success_msg != '':
            self.request.session.flash(success_msg, queue=Notification.SUCCESS)
        if error_msg != '':
            self.request.session.flash(error_msg, queue=Notification.ERROR)
        return

    def image_remove_deleted_launch_permissions(self, new_launch_permissions):
        success_msg = ''
        error_msg = ''
        for lp in self.image_launch_permissions:
            is_deleted = True
            for new_lp in new_launch_permissions:
                if lp == new_lp:
                    is_deleted = False
            if is_deleted:
                (msg, queue) = self.image_remove_launch_permission(lp)
                if queue is Notification.SUCCESS:
                    success_msg += msg + " "
                else:
                    error_msg += msg + " "

        if success_msg != '':
            self.request.session.flash(success_msg, queue=Notification.SUCCESS)
        if error_msg != '':
            self.request.session.flash(error_msg, queue=Notification.ERROR)
        return

    def image_add_launch_permission(self, lp):
        try:
            self.log_request(_(u"Adding accountID {0} to launch permissions").format(lp))
            self.image.set_launch_permissions(lp)
            msg_template = _(u'Successfully added accountID {lp}')
            msg = msg_template.format(lp=lp)
            queue = Notification.SUCCESS
        except BotoServerError as err:
            msg = err.message
            queue = Notification.ERROR
        return msg, queue

    def image_remove_launch_permission(self, lp):
        try:
            self.log_request(_(u"Removing accountID {0} from launch permissions").format(lp))
            self.image.remove_launch_permissions(lp)
            msg_template = _(u'Successfully removed accountID {lp}')
            msg = msg_template.format(lp=lp)
            queue = Notification.SUCCESS
        except BotoServerError as err:
            msg = err.message
            queue = Notification.ERROR
        return msg, queue

    @view_config(route_name='image_deregister', request_method='POST')
    def image_deregister(self):
        if self.deregister_form.validate():
            with boto_error_handler(self.request):
                delete_snapshot = False
                if self.image.root_device_type == 'ebs' and self.request.params.get('delete_snapshot') == 'y':
                    delete_snapshot = True
                self.conn.deregister_image(self.image.id, delete_snapshot=delete_snapshot)
                ImagesView.invalidate_images_cache()  # clear images cache
                location = self.request.route_path('images')
                msg = _(u'Successfully sent request to deregistered image.')
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

    @staticmethod
    def get_image_name_id(image):
        """Return the name (ID) of an image, with the name lookup performed via the "Name" tag, falling back
        to the image name if missing.
        """
        if image is None:
            return ''
        name_tag = image.tags.get('Name')
        if name_tag is None and not image.name:
            return image.id
        return '{0} ({1})'.format(name_tag or image.name, image.id)

    def get_display_name(self, escapebraces=True):
        if self.image:
            return TaggedItemView.get_display_name(self.image, escapebraces=escapebraces)
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

    @staticmethod
    def get_image_snapshot_id(image):
        """Get the snapshot id from the image BDM (for EBS images only)"""
        if image.root_device_type == 'ebs':
            bdm_values = image.block_device_mapping.values()
            if bdm_values:
                return getattr(bdm_values[0], 'snapshot_id', None)
