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
import simplejson as json

from beaker.cache import cache_region, cache_managers
from boto.exception import BotoServerError
from boto.ec2.image import Image
from boto.s3.key import Key
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from ..constants.images import PLATFORM_CHOICES, PlatformChoice
from ..forms.images import ImageForm, ImagesFiltersForm, DeregisterImageForm
from ..i18n import _
from ..models import Notification
from ..models.auth import User
from ..views import LandingPageView, TaggedItemView, JSONResponse
from . import boto_error_handler
from ..layout import __version__ as curr_version

import panels

class ImageBundlingMixin(object):
    """
    This has the code necessary to handle image bundling tasks attached to an instance.
    It checks state and completes the registration if possible. Otherwise, it creates
    a fake image that acts as a placeholder so that users can see status.
    """
    def handle_instance_being_bundled(self, instance, do_not_finish=False):
        bundling_tag = instance.tags.get('ec_bundling') or None
        if bundling_tag is None:
            return None
        bucket, bundle_id = bundling_tag.split('/')
        s3_conn = self.get_connection(conn_type='s3')
        k = Key(s3_conn.get_bucket(bucket))
        k.key = bundle_id
        metadata = json.loads(k.get_contents_as_string())
        tasks = self.conn.get_all_bundle_tasks([bundle_id])
        if do_not_finish and len(tasks) > 0:
            tasks[0].state = 'pending'
        if len(tasks) == 0 or tasks[0].state == 'complete':
            # handle registration
            if metadata['version'] != curr_version:
                self.log_request(_(u"Bundle operation {0} from previous software version will be ignored.").format(bundle_id))
            else:
                self.log_request(_(u"Registering image from bundle operation {0}").format(bundle_id))
                image_id = self.conn.register_image(
                                name=metadata['name'],
                                description=metadata['description'],
                                image_location="%s/%s.manifest.xml" % (bucket, metadata['prefix']),
                                virtualization_type=metadata['virt_type'],
                                kernel_id=metadata['kernel_id'],
                                ramdisk_id=metadata['ramdisk_id']
                           )
            # cleanup creds
            iam_conn = self.get_connection(conn_type='iam')
            iam_conn.delete_access_key(metadata['access'])
            # cleanup metadata
            k.delete()
            self.conn.delete_tags(instance.id, ['ec_bundling'])
            return self.conn.get_all_images(image_ids=[image_id])[0]
        elif tasks[0].state == 'failed':
            # generate error message, need to let user know somehow
            logging.warn("bundle task failed! " + tasks[0].message)
            # cleanup creds
            iam_conn = self.get_connection(conn_type='iam')
            iam_conn.delete_access_key(metadata['access'])
            # cleanup metadata
            k.delete()
            self.conn.delete_tags(instance.id, ['ec_bundling'])
            return None
        elif tasks[0].state in ['pending', 'bundling', 'storing']:
            # add this into image list
            fakeimage = Image()
            fakeimage.id=_(u'Pending')
            fakeimage.location="%s/%s.manifest.xml" % (bucket, metadata['prefix'])
            fakeimage.owner_id=''  # do we need this?
            fakeimage.state=tasks[0].state
            fakeimage.progress=tasks[0].progress
            fakeimage.is_public=False
            fakeimage.name=metadata['name']
            fakeimage.description=metadata['description']
            fakeimage.architecture=metadata['arch']
            fakeimage.platform='windows' if metadata['platform'] == 'windows' else None
            fakeimage.type='machine'
            fakeimage.root_device_type='instance-store'
            fakeimage.root_device_name='/dev/sda'
            fakeimage.block_device_mapping = {}
            return fakeimage

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
    def invalidate_images_cache():
        for manager in cache_managers.values():
            if '_get_images_cache' in manager.namespace.namespace:
                manager.clear()


class ImagesJsonView(LandingPageView, ImageBundlingMixin):

    def __init__(self, request):
        super(ImagesJsonView, self).__init__(request)
        self.conn = self.get_connection()

    """Images returned as JSON"""
    @view_config(route_name='images_json', renderer='json', request_method='POST')
    def images_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        # actual images
        items = self.get_items()
        # fetch instances that have been marked for bundling
        instances = self.conn.get_only_instances(filters={'tag-key':'ec_bundling'})
        for instance in instances:
            image = self.handle_instance_being_bundled(instance)
            if image is not None:
                items.append(image)
        # Apply filters, skipping owner_alias since it's leveraged in self.get_items() below
        filtered_items = self.filter_items(items, ignore=['owner_alias', 'platform'])
        if self.request.params.getall('platform'):
            filtered_items = self.filter_by_platform(filtered_items)
        images = []
        for image in filtered_items:
            platform = ImageView.get_platform(image)
            images.append(dict(
                architecture=image.architecture,
                description=image.description,
                id=image.id,
                name=image.name,
                state=image.state,
                transitional=image.state not in ['available', 'failed', 'deleted'],
                progress=0,  # this is valid for transitional images till we get something better
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
            image = self.conn.get_image(image_id)
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

    @view_config(route_name='image_state_json', renderer='json', request_method='POST')
    def image_state_json(self):
        image_id = self.request.matchdict.get('id')
        with boto_error_handler(self.request):
            url = None
            if image_id.find('pi-') == 0:
                instances = self.conn.get_only_instances([image_id[1:]])
                image = self.handle_instance_being_bundled(instances[0])
                if image.state == 'available':
                    url = self.request.route_path('image_view', id=image.id)
            else:
                image = self.conn.get_image(image_id)
            """Return current image status"""
            image_status = image.state if image else 'deleted'
            return dict(
                results=dict(image_status=image_status, url=url)
            )

    def get_items(self):
        owner_alias = self.request.params.get('owner_alias')
        if not owner_alias and self.cloud_type == 'aws':
            # Set default alias to 'amazon' for AWS
            owner_alias = 'amazon'
        owners = [owner_alias] if owner_alias else []
        region = self.request.session.get('region')
        items = self.get_images(self.conn, owners, [], region)
        # This is to included shared images in the owned images list per GUI-374
        if owner_alias == 'self':
            items.extend(self.get_images(self.conn, [], ['self'], region))
        return items

    def get_images(self, conn, owners, executors, region):
        """Get images, leveraging Beaker cache for long_term duration (3600 seconds)"""
        if 'amazon' in owners or 'aws-marketplace' in owners:
            cache_key = 'images_cache_{owners}_{executors}_{region}'.format(
                owners=owners, executors=executors, region=region)

            # Heads up!  Update cache key if we allow filters to be passed here
            @cache_region('long_term', cache_key)
            def _get_images_cache(_owners, _executors, _region):
                with boto_error_handler(self.request):
                    filters = {'image-type': 'machine'}
                    return conn.get_all_images(owners=_owners, executable_by=_executors, filters=filters) if conn else []
            return _get_images_cache(owners, executors, region)
        else:
            with boto_error_handler(self.request):
                filters = {'image-type': 'machine'}
                return conn.get_all_images(owners=owners, executable_by=executors, filters=filters) if conn else []

    def filter_by_platform(self, items):
        filtered_items = []
        for item in items:
            for platform in self.request.params.getall('platform'):
                if self.cloud_type == 'euca' and platform == 'linux':
                    platform = ''
                if item.platform == platform:
                    filtered_items.append(item)
        return filtered_items


class ImageView(TaggedItemView, ImageBundlingMixin):
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
        image_id = self.image.id if self.image is not None else ''
        if self.image is not None and self.image.state != 'available':
            image_id = self.request.matchdict.get('id').encode('ascii', 'ignore')
        self.render_dict = dict(
            image=self.image,
            image_id=image_id,
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
                if image_param.find('pi-') == 0:
                    instances = self.conn.get_only_instances([image_param[1:]])
                    images = [self.handle_instance_being_bundled(instances[0], do_not_finish=True)]
                else:
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
            ImagesView.invalidate_images_cache()

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
