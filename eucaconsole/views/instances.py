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
Pyramid views for Eucalyptus and AWS instances

"""
import base64
from operator import attrgetter
import simplejson as json
from M2Crypto import RSA
import re

from boto.exception import BotoServerError
from boto.s3.key import Key
from boto.ec2.bundleinstance import BundleInstanceTask
from boto.ec2.networkinterface import NetworkInterfaceCollection, NetworkInterfaceSpecification

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config

from ..forms.images import ImagesFiltersForm
from ..forms.instances import (
    InstanceForm, AttachVolumeForm, DetachVolumeForm, LaunchInstanceForm, LaunchMoreInstancesForm,
    RebootInstanceForm, StartInstanceForm, StopInstanceForm, TerminateInstanceForm, InstanceCreateImageForm,
    BatchTerminateInstancesForm, InstancesFiltersForm, InstanceTypeForm,
    AssociateIpToInstanceForm, DisassociateIpFromInstanceForm)
from ..forms import GenerateFileForm
from ..forms.keypairs import KeyPairForm
from ..forms.securitygroups import SecurityGroupForm
from ..i18n import _
from ..models import Notification
from ..views import BaseView, LandingPageView, TaggedItemView, BlockDeviceMappingItemView, JSONResponse
from ..views.images import ImageView
from ..views.roles import RoleView
from ..views.securitygroups import SecurityGroupsView
from . import boto_error_handler
from . import guess_mimetype_from_buffer
from ..layout import __version__ as curr_version


class BaseInstanceView(BaseView):
    """Base class for instance-related views"""
    def __init__(self, request):
        super(BaseInstanceView, self).__init__(request)
        self.conn = self.get_connection()
        self.vpc_conn = self.get_connection(conn_type='vpc')

    def get_instance(self, instance_id=None):
        instance_id = instance_id or self.request.matchdict.get('id')
        if instance_id:
            try:
                reservations_list = self.conn.get_all_reservations(instance_ids=[instance_id])
                reservation = reservations_list[0] if reservations_list else None
                if reservation:
                    instance = reservation.instances[0]
                    instance.reservation_id = reservation.id
                    instance.owner_id = reservation.owner_id
                    if instance.platform is None:
                        instance.platform = _(u"linux")
                    if instance.vpc_id:
                        vpc = self.vpc_conn.get_all_vpcs(vpc_ids=[instance.vpc_id])[0]
                        instance.vpc_name = TaggedItemView.get_display_name(vpc, escapebraces=True)
                    else:
                        instance.vpc_name = ''
                    instance.instance_profile_id = None
                    if instance.instance_profile is not None and len(instance.instance_profile.keys()) > 0:
                        instance.instance_profile_id = instance.instance_profile.keys()[0]
                    return instance
            except BotoServerError as err:
                pass
        return None

    def get_image(self, instance=None, image_id=None):
        image_id = instance.image_id if instance else image_id
        if image_id is None:
            image_id = self.request.matchdict.get('image_id') or self.request.params.get('image_id')
        if self.conn and image_id:
            try:
                image = self.conn.get_image(image_id)
                if image:
                    platform = ImageView.get_platform(image)
                    image.platform_name = ImageView.get_platform_name(platform)
                return image
            except BotoServerError as err:
                pass
        return None

    def get_vpc_subnet_display(self, subnet_id):
        if self.vpc_conn and subnet_id:
            with boto_error_handler(self.request):
                vpc_subnet = self.vpc_conn.get_all_subnets(subnet_ids=[subnet_id])
                if vpc_subnet:
                    return "{0} ({1})".format(vpc_subnet[0].cidr_block, subnet_id)
        return ''


class InstancesView(LandingPageView, BaseInstanceView):
    def __init__(self, request):
        super(InstancesView, self).__init__(request)
        self.initial_sort_key = '-launch_time'
        self.prefix = '/instances'
        self.json_items_endpoint = self.get_json_endpoint('instances_json')
        self.location = self.get_redirect_location('instances')
        self.iam_conn = self.get_connection(conn_type="iam")
        self.start_form = StartInstanceForm(self.request, formdata=self.request.params or None)
        self.stop_form = StopInstanceForm(self.request, formdata=self.request.params or None)
        self.reboot_form = RebootInstanceForm(self.request, formdata=self.request.params or None)
        self.terminate_form = TerminateInstanceForm(self.request, formdata=self.request.params or None)
        self.batch_terminate_form = BatchTerminateInstancesForm(self.request, formdata=self.request.params or None)
        self.associate_ip_form = AssociateIpToInstanceForm(
            self.request, conn=self.conn, formdata=self.request.params or None)
        self.disassociate_ip_form = DisassociateIpFromInstanceForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            start_form=self.start_form,
            stop_form=self.stop_form,
            reboot_form=self.reboot_form,
            terminate_form=self.terminate_form,
            batch_terminate_form=self.batch_terminate_form,
            associate_ip_form=self.associate_ip_form,
            disassociate_ip_form=self.disassociate_ip_form,
        )

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt')
    def instances_landing(self):
        filter_keys = [
            'id', 'name', 'image_id', 'instance_type', 'ip_address', 'key_name', 'placement',
            'root_device', 'security_groups_string', 'state', 'tags', 'roles', 'vpc_id', 'subnet_id']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='launch_time', name=_(u'Launch time: Oldest to Newest')),
            dict(key='-launch_time', name=_(u'Launch time: Newest to Oldest')),
            dict(key='id', name=_(u'Instance ID')),
            dict(key='name', name=_(u'Instance name: A to Z')),
            dict(key='-name', name=_(u'Instance name: Z to A')),
            dict(key='placement', name=_(u'Availability zone')),
            dict(key='key_name', name=_(u'Key pair')),
        ]
        autoscale_conn = self.get_connection(conn_type='autoscale')
        iam_conn = self.get_connection(conn_type='iam')
        vpc_conn = self.get_connection(conn_type='vpc')
        filters_form = InstancesFiltersForm(
            self.request, ec2_conn=self.conn, autoscale_conn=autoscale_conn,
            iam_conn=iam_conn, vpc_conn=vpc_conn,
            cloud_type=self.cloud_type, formdata=self.request.params or None)
        self.render_dict.update(dict(
            filter_fields=True,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            json_items_endpoint=self.json_items_endpoint,
            filters_form=filters_form,
        ))
        return self.render_dict

    @view_config(route_name='instances_start', request_method='POST')
    def instances_start(self):
        instance_id = self.request.params.get('instance_id')
        if self.start_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Starting instance {0}").format(instance_id))
                # Can only start an instance if it has a volume attached
                self.conn.start_instances([instance_id])
                msg = _(u'Successfully sent start instance request.  It may take a moment to start the instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            msg = _(u'Unable to start instance')
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @view_config(route_name='instances_stop', request_method='POST')
    def instances_stop(self):
        instance_id = self.request.params.get('instance_id')
        instance = self.get_instance(instance_id)
        if instance and self.stop_form.validate():
            # Only EBS-backed instances can be stopped
            if instance.root_device_type == 'ebs':
                with boto_error_handler(self.request, self.location):
                    self.log_request(_(u"Stopping instance {0}").format(instance_id))
                    instance.stop()
                    msg = _(u'Successfully sent stop instance request.  It may take a moment to stop the instance.')
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
            else:
                msg = _(u'Only EBS-backed instances can be stopped')
                self.request.session.flash(msg, queue=Notification.ERROR)
        else:
            msg = _(u'Unable to stop instance')
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @view_config(route_name='instances_reboot', request_method='POST')
    def instances_reboot(self):
        instance_id = self.request.params.get('instance_id')
        if self.reboot_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Rebooting instance {0}").format(instance_id))
                rebooted = self.conn.reboot_instances([instance_id])
                msg = _(u'Successfully sent reboot request.  It may take a moment to reboot the instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                if not rebooted:
                    msg = _(u'Unable to reboot the instance.')
                    self.request.session.flash(msg, queue=Notification.ERROR)
        else:
            msg = _(u'Unable to reboot instance')
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @view_config(route_name='instances_terminate', request_method='POST')
    def instances_terminate(self):
        instance_id = self.request.params.get('instance_id')
        if self.terminate_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Terminating instance {0}").format(instance_id))
                self.conn.terminate_instances([instance_id])
                msg = _(
                    u'Successfully sent terminate instance request.  It may take a moment to shut down the instance.')
                if self.request.is_xhr:
                    return JSONResponse(status=200, message=msg)
                else:
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            msg = _(u'Unable to terminate instance')
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @view_config(route_name='instances_batch_terminate', request_method='POST')
    def instances_batch_terminate(self):
        instance_ids = self.request.params.getall('instance_ids')
        if self.batch_terminate_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Terminating instances {0}").format(str(instance_ids)))
                self.conn.terminate_instances(instance_ids=instance_ids)
                prefix = _(u'Successfully sent request to terminate the following instances:')
                msg = '{0} {1}'.format(prefix, ', '.join(instance_ids))
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            msg = _(u'Unable to terminate instances')
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @view_config(route_name='instances_associate', request_method='POST')
    def instances_associate_ip_address(self):
        instance_id = self.request.params.get('instance_id')
        if self.associate_ip_form.validate():
            with boto_error_handler(self.request, self.location):
                new_ip = self.request.params.get('ip_address')
                self.log_request(_(u"Associating IP {0} with instances {1}").format(new_ip, instance_id))
                self.conn.associate_address(instance_id, new_ip)
                msg = _(u'Successfully associated the IP to the instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        return self.render_dict

    @view_config(route_name='instances_disassociate', request_method='POST')
    def instances_disassociate_ip_address(self):
        if self.disassociate_ip_form.validate():
            with boto_error_handler(self.request, self.location):
                ip_address = self.request.params.get('ip_address')
                self.log_request(_(u"Disassociating IP {0}").format(ip_address))
                self.conn.disassociate_address(ip_address)
                msg = _(u'Successfully disassociated the IP from the instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        return self.render_dict


class InstancesJsonView(LandingPageView):
    def __init__(self, request):
        super(InstancesJsonView, self).__init__(request)
        self.conn = self.get_connection()
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.vpcs = self.get_all_vpcs()
        self.keypairs = self.get_all_keypairs()

    @view_config(route_name='instances_json', renderer='json', request_method='POST')
    def instances_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        instances = []
        filters = {}
        availability_zone_param = self.request.params.getall('availability_zone')
        if availability_zone_param:
            filters.update({'availability-zone': availability_zone_param})
        instance_state_param = self.request.params.getall('state')
        if instance_state_param:
            filters.update({'instance-state-name': instance_state_param})
        instance_type_param = self.request.params.getall('instance_type')
        if instance_type_param:
            filters.update({'instance-type': instance_type_param})
        security_group_param = self.request.params.getall('security_group')
        if security_group_param:
            filters.update({'group-name': [self.unescape_braces(sg) for sg in security_group_param]})
        root_device_type_param = self.request.params.getall('root_device_type')
        if root_device_type_param:
            filters.update({'root-device-type': root_device_type_param})
        # Don't filter by these request params in Python, as they're included in the "filters" params sent to the CLC
        # Note: the choices are from attributes in InstancesFiltersForm
        ignore_params = [
            'availability_zone', 'instance_type', 'state', 'security_group',
            'scaling_group', 'root_device_type', 'roles']
        filtered_items = self.filter_items(self.get_items(filters=filters), ignore=ignore_params)
        if self.request.params.get('scaling_group'):
            filtered_items = self.filter_by_scaling_group(filtered_items)
        if self.request.params.get('roles'):
            filtered_items = self.filter_by_roles(filtered_items)
        transitional_states = ['pending', 'stopping', 'shutting-down']
        elastic_ips = [ip.public_ip for ip in self.conn.get_all_addresses()]
        owner_alias = None
        if not owner_alias and self.cloud_type == 'aws':
            # Set default alias to 'amazon' for AWS
            owner_alias = 'amazon'
        region = self.request.session.get('region')
        for instance in filtered_items:
            is_transitional = instance.state in transitional_states
            security_groups_array = sorted({'name': group.name, 'id': group.id} for group in instance.groups)
            if instance.platform is None:
                instance.platform = _(u"linux")
            has_elastic_ip = instance.ip_address in elastic_ips
            exists_key = True if self.get_keypair_by_name(instance.key_name) else False
            instances.append(dict(
                id=instance.id,
                name=TaggedItemView.get_display_name(instance, escapebraces=False),
                instance_type=instance.instance_type,
                image_id=instance.image_id,
                ip_address=instance.ip_address,
                has_elastic_ip=has_elastic_ip,
                public_dns_name=instance.public_dns_name,
                launch_time=instance.launch_time,
                placement=instance.placement,
                platform=instance.platform,
                root_device=instance.root_device_type,
                security_groups=security_groups_array,
                key_name=instance.key_name,
                exists_key=exists_key,
                vpc_name=instance.vpc_name,
                status=instance.state,
                tags=TaggedItemView.get_tags_display(instance.tags),
                transitional=is_transitional,
                running_create=True if instance.tags.get('ec_bundling') else False,
            ))
        image_ids = [i['image_id'] for i in instances]
        images = self.conn.get_all_images(filters={'image-id': image_ids})
        for instance in instances:
            image = self.get_image_by_id(images, instance['image_id'])
            image_name = None
            if image:
                image_name = '{0}{1}'.format(
                    image.name if image.name else image.id,
                    ' ({0})'.format(image.id) if image.name else ''
                )
            instance['image_name'] = image_name
        return dict(results=instances)

    def get_items(self, filters=None):
        if self.conn:
            instances = []
            with boto_error_handler(self.request):
                for reservation in self.conn.get_all_reservations(filters=filters):
                    for instance in reservation.instances:
                        if instance.vpc_id:
                            vpc = self.get_vpc_by_id(instance.vpc_id)
                            instance.vpc_name = TaggedItemView.get_display_name(vpc)
                        else:
                            instance.vpc_name = ''
                        instances.append(instance)
            return instances
        return []

    def get_all_vpcs(self):
        return self.vpc_conn.get_all_vpcs() if self.vpc_conn else []

    def get_vpc_by_id(self, vpc_id):
        for vpc in self.vpcs:
            if vpc_id == vpc.id:
                return vpc

    def get_all_keypairs(self):
        return self.conn.get_all_key_pairs() if self.conn else []

    def get_keypair_by_name(self, keypair_name):
        for keypair in self.keypairs:
            if keypair_name == keypair.name:
                return keypair

    @staticmethod
    def get_image_by_id(images, image_id):
        if images:
            for image in images:
                if image.id == image_id:
                    return image
        return None

    def filter_by_scaling_group(self, items):
        filtered_items = []
        for item in items:
            autoscaling_tag = item.tags.get('aws:autoscaling:groupName')
            if autoscaling_tag:
                for scaling_group in self.request.params.getall('scaling_group'):
                    if autoscaling_tag == self.unescape_braces(scaling_group):
                        filtered_items.append(item)
        return filtered_items

    def filter_by_roles(self, items):
        iam_conn = self.get_connection(conn_type="iam")
        filtered_items = []
        profiles = []
        for role in self.request.params.getall('roles'):
            instance_profiles_list = iam_conn.list_instance_profiles(
                path_prefix='/'+role).list_instance_profiles_response.list_instance_profiles_result.instance_profiles
            for profile in instance_profiles_list:
                profiles.append(profile.instance_profile_id)
        for item in items:
            if len(item.instance_profile) > 0 and item.instance_profile['id'] in profiles:
                filtered_items.append(item)
        return filtered_items


class InstanceJsonView(BaseInstanceView):
    def __init__(self, request):
        super(InstanceJsonView, self).__init__(request)

    @view_config(route_name='instance_json', renderer='json', request_method='GET')
    def instance_json(self):
        instance = self.get_instance()
        # Only included a few fields here. Feel free to include more as needed.
        return dict(results=dict(
                    id=instance.id,
                    instance_type=instance.instance_type,
                    image_id=instance.image_id,
                    platform=instance.platform,
                    state_reason=instance.state_reason,
                    ip_address=instance.ip_address,
                    root_device_name=instance.root_device_name,
                    root_device_type=instance.root_device_type,
               ))


class InstanceView(TaggedItemView, BaseInstanceView):
    VIEW_TEMPLATE = '../templates/instances/instance_view.pt'

    def __init__(self, request):
        super(InstanceView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.iam_conn = self.get_connection(conn_type="iam")
        self.instance = self.get_instance()
        self.image = self.get_image(self.instance)
        self.scaling_group = self.get_scaling_group()
        self.instance_form = InstanceForm(
            self.request, instance=self.instance, conn=self.conn, formdata=self.request.params or None)
        self.start_form = StartInstanceForm(self.request, formdata=self.request.params or None)
        self.stop_form = StopInstanceForm(self.request, formdata=self.request.params or None)
        self.reboot_form = RebootInstanceForm(self.request, formdata=self.request.params or None)
        self.terminate_form = TerminateInstanceForm(self.request, formdata=self.request.params or None)
        self.associate_ip_form = AssociateIpToInstanceForm(
            self.request, conn=self.conn, formdata=self.request.params or None)
        self.disassociate_ip_form = DisassociateIpFromInstanceForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.instance
        self.location = self.get_redirect_location()
        self.instance_name = TaggedItemView.get_display_name(self.instance)
        self.security_groups_array = sorted(
            {'name': group.name, 'id': group.id} for group in self.instance.groups) if self.instance else []
        self.instance_keypair = self.instance.key_name if self.instance else ''
        self.has_elastic_ip = self.check_has_elastic_ip(self.instance.ip_address) if self.instance else False
        self.role = None
        if self.instance and self.instance.instance_profile:
            arn = self.instance.instance_profile['arn']
            profile_name = arn[(arn.rindex('/')+1):]
            inst_profile = self.iam_conn.get_instance_profile(profile_name)
            self.role = inst_profile.roles.member.role_name
        self.running_create = False
        if self.instance:
            self.running_create = True if self.instance.tags.get('ec_bundling') else False

        self.render_dict = dict(
            instance=self.instance,
            instance_name=self.instance_name,
            instance_security_groups=self.get_security_group_list_string(),
            instance_keypair=self.instance_keypair,
            image=self.image,
            scaling_group=self.scaling_group,
            instance_form=self.instance_form,
            start_form=self.start_form,
            stop_form=self.stop_form,
            reboot_form=self.reboot_form,
            terminate_form=self.terminate_form,
            associate_ip_form=self.associate_ip_form,
            disassociate_ip_form=self.disassociate_ip_form,
            has_elastic_ip=self.has_elastic_ip,
            vpc_subnet_display=self.get_vpc_subnet_display(self.instance.subnet_id) if self.instance else None,
            role=self.role,
            running_create=self.running_create,
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='instance_view', renderer=VIEW_TEMPLATE, request_method='GET')
    def instance_view(self):
        if self.instance is None:
            raise HTTPNotFound()
        return self.render_dict

    @view_config(route_name='instance_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_update(self):
        if self.instance and self.instance_form.validate():

            with boto_error_handler(self.request, self.location):
                # Update tags
                self.update_tags()

                # Save Name tag
                name = self.request.params.get('name', '')
                self.update_name_tag(name)

                # Update stopped instance
                if self.instance.state == 'stopped':
                    instance_type = self.request.params.get('instance_type')
                    kernel = self.request.params.get('kernel')
                    ramdisk = self.request.params.get('ramdisk')
                    self.log_request(_(u"Updating instance {0} (type={1}, kernel={2}, ramidisk={3})").format(
                        self.instance.id, instance_type, kernel, ramdisk))
                    if self.instance.instance_type != instance_type:
                        self.conn.modify_instance_attribute(self.instance.id, 'instanceType', instance_type)
                    user_data = self.get_user_data()
                    if user_data is not None:
                        self.conn.modify_instance_attribute(self.instance.id, 'userData', base64.b64encode(user_data))
                    if kernel != '' and self.instance.kernel != kernel:
                        self.conn.modify_instance_attribute(self.instance.id, 'kernel', kernel)
                    if ramdisk != '' and self.instance.ramdisk != ramdisk:
                        self.conn.modify_instance_attribute(self.instance.id, 'ramdisk', ramdisk)

                # Start instance if desired
                if self.request.params.get('start_later'):
                    self.log_request(_(u"Starting instance {0}").format(self.instance.id))
                    self.instance.start()

                msg = _(u'Successfully modified instance')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                return HTTPFound(location=self.location)
        return self.render_dict

    @view_config(route_name='instance_start', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_start(self):
        if self.instance and self.start_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Starting instance {0}").format(self.instance.id))
                # Can only start an instance if it has a volume attached
                self.instance.start()
                msg = _(u'Successfully sent start instance request.  It may take a moment to start the instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        return self.render_dict

    @view_config(route_name='instance_stop', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_stop(self):
        if self.instance and self.stop_form.validate():
            # Only EBS-backed instances can be stopped
            if self.image.root_device_type == 'ebs':
                with boto_error_handler(self.request, self.location):
                    self.log_request(_(u"Stopping instance {0}").format(self.instance.id))
                    self.instance.stop()
                    msg = _(u'Successfully sent stop instance request.  It may take a moment to stop the instance.')
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                return HTTPFound(location=self.location)
        return self.render_dict

    @view_config(route_name='instance_reboot', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_reboot(self):
        location = self.request.route_path('instance_view', id=self.instance.id)
        if self.instance and self.reboot_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Rebooting instance {0}").format(self.instance.id))
                rebooted = self.instance.reboot()
                msg = _(u'Successfully sent reboot request.  It may take a moment to reboot the instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                if not rebooted:
                    msg = _(u'Unable to reboot the instance.')
                    self.request.session.flash(msg, queue=Notification.ERROR)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='instance_terminate', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_terminate(self):
        if self.instance and self.terminate_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Terminating instance {0}").format(self.instance.id))
                self.instance.terminate()
                msg = _(
                    u'Successfully sent terminate instance request.  It may take a moment to shut down the instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        return self.render_dict

    @view_config(route_name='instance_get_password', request_method='POST', renderer='json')
    def instance_get_password(self):
        if not self.is_csrf_valid():
            return JSONResponse(status=400, message="missing CSRF token")
        instance_id = self.request.matchdict.get('id')
        with boto_error_handler(self.request, self.location):
            try:
                passwd_data = self.conn.get_password_data(instance_id)
                priv_key_string = self.request.params.get('key')
                priv_key_string = base64.b64decode(priv_key_string)
                user_priv_key = RSA.load_key_string(priv_key_string)
                string_to_decrypt = base64.b64decode(passwd_data)
                ret = user_priv_key.private_decrypt(string_to_decrypt, RSA.pkcs1_padding)
                return dict(results=dict(instance=instance_id, password=ret))
            except RSA.RSAError as err:  # likely, bad key
                return JSONResponse(status=400, message=_(
                    u"There was a problem with the key, please try again, verifying the correct private key is used."))

    @view_config(route_name='instance_associate', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_associate_ip_address(self):
        if self.instance and self.associate_ip_form.validate():
            with boto_error_handler(self.request, self.location):
                new_ip = self.request.params.get('ip_address')
                self.instance.use_ip(new_ip)
                msg = _(u'Successfully associated the IP to the instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        return self.render_dict

    @view_config(route_name='instance_disassociate', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_disassociate_ip_address(self):
        if self.disassociate_ip_form.validate():
            with boto_error_handler(self.request, self.location):
                ip_address = self.request.params.get('ip_address')
                ip_addresses = self.conn.get_all_addresses(addresses=[ip_address])
                elastic_ip = ip_addresses[0] if ip_addresses else None
                if elastic_ip:
                    elastic_ip.disassociate()
                msg = _(u'Successfully disassociated the IP from the instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        return self.render_dict

    def get_scaling_group(self):
        if self.instance:
            return self.instance.tags.get('aws:autoscaling:groupName')
        return None

    def get_security_group_list_string(self):
        security_group_list = [] 
        if self.instance:
            instance_groups = self.instance.groups
            if instance_groups:
                for sgroup in instance_groups:
                    security_group_list.append(sgroup.id) 
        return ','.join(security_group_list) 

    def get_redirect_location(self):
        if self.instance:
            return self.request.route_path('instance_view', id=self.instance.id)
        return ''

    def disassociate_ip_address(self, ip_address=None):
        ip_addresses = self.conn.get_all_addresses(addresses=[ip_address])
        elastic_ip = ip_addresses[0] if ip_addresses else None
        if elastic_ip:
            self.log_request(_(u"Disassociating ip {0} from instance {1}").format(ip_address, self.instance.id))
            elastic_ip.disassociate()

    def check_has_elastic_ip(self, ip_address):
        has_elastic_ip = False
        elastic_ips = self.conn.get_all_addresses()
        if ip_address is not None:
            for ip in elastic_ips:
                if ip_address == ip.public_ip:
                    has_elastic_ip = True
        return has_elastic_ip

    def get_controller_options_json(self):
        if not self.instance:
            return ''
        return BaseView.escape_json(json.dumps({
            'instance_state_json_url': self.request.route_path('instance_state_json', id=self.instance.id),
            'instance_userdata_json_url': self.request.route_path('instance_userdata_json', id=self.instance.id),
            'instance_ip_address_json_url': self.request.route_path('instance_ip_address_json', id=self.instance.id),
            'instance_console_json_url': self.request.route_path('instance_console_output_json', id=self.instance.id),
            'instance_state': self.instance.state,
            'instance_id': self.instance.id,
            'instance_ip_address': self.instance.ip_address,
            'instance_public_dns': self.instance.public_dns_name,
            'instance_platform': self.instance.platform,
            'instance_security_groups': self.security_groups_array,
            'instance_keypair': self.instance_keypair,
            'has_elastic_ip': self.has_elastic_ip,
        }))


class InstanceStateView(BaseInstanceView):
    def __init__(self, request):
        super(InstanceStateView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.instance = self.get_instance()

    @view_config(route_name='instance_state_json', renderer='json', request_method='GET')
    def instance_state_json(self):
        """Return current instance state"""
        return dict(results=self.instance.state)

    @view_config(route_name='instance_userdata_json', renderer='json', request_method='GET')
    def instance_userdata_json(self):
        """Return current instance state"""
        with boto_error_handler(self.request):
            user_data = self.conn.get_instance_attribute(self.instance.id, 'userData')
            if 'userData' in user_data.keys():
                user_data = user_data['userData']
                unencoded = base64.b64decode(user_data) if user_data is not None else ''
                mime_type = guess_mimetype_from_buffer(unencoded, mime=True)
                if mime_type.find('text') == 0:
                    user_data = unencoded
                else:
                    # get more descriptive text
                    mime_type = guess_mimetype_from_buffer(unencoded)
                    user_data = None
            else:
                user_data = ''
                mime_type = ''
            return dict(results=dict(type=mime_type, data=user_data))

    @view_config(route_name='instance_ip_address_json', renderer='json', request_method='GET')
    def instance_ip_address_json(self):
        """Return current instance state"""
        has_elastic_ip = self.check_has_elastic_ip(self.instance.ip_address) if self.instance else False
        ip_address_dict = dict(
            ip_address=self.instance.ip_address,
            public_dns_name=self.instance.public_dns_name,
            private_ip_address=self.instance.private_ip_address,
            private_dns_name=self.instance.private_dns_name,
            has_elastic_ip=has_elastic_ip,
        )
        return ip_address_dict

    @view_config(route_name='instance_nextdevice_json', renderer='json', request_method='GET')
    def instance_nextdevice_json(self):
        """Return current instance state"""
        return dict(results=self.suggest_next_device_name(self.instance))

    @view_config(route_name='instance_console_output_json', renderer='json', request_method='GET')
    def instance_console_output_json(self):
        """Return console output for instance"""
        with boto_error_handler(self.request):
            output = self.conn.get_console_output(instance_id=self.instance.id)
        return dict(results=base64.b64encode(output.output))

    # TODO: also in forms/instances.py, let's consolidate
    def suggest_next_device_name(self, instance):
        mappings = instance.block_device_mapping
        for i in range(0, 10):   # Test names with char 'f' to 'p'
            dev_name = '/dev/sd'+str(unichr(102+i))
            try:
                mappings[dev_name]
            except KeyError:
                return dev_name
        return 'error'

    def check_has_elastic_ip(self, ip_address):
        has_elastic_ip = False
        elastic_ips = self.conn.get_all_addresses()
        if ip_address is not None:
            for ip in elastic_ips:
                if ip_address == ip.public_ip:
                    has_elastic_ip = True
        return has_elastic_ip


class InstanceVolumesView(BaseInstanceView):
    VIEW_TEMPLATE = '../templates/instances/instance_volumes.pt'

    def __init__(self, request):
        super(InstanceVolumesView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        # fetching all volumes all the time is inefficient. should re-factor in the future
        self.volumes = []
        self.location = self.request.route_path('instance_volumes', id=self.request.matchdict.get('id'))
        with boto_error_handler(request, self.location):
            self.volumes = self.conn.get_all_volumes()
        self.instance = self.get_instance()
        self.attach_form = AttachVolumeForm(
            self.request, volumes=self.volumes, instance=self.instance, formdata=self.request.params or None)
        self.instance_name = TaggedItemView.get_display_name(self.instance)
        self.detach_form = DetachVolumeForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            instance=self.instance,
            instance_name=self.instance_name,
            attach_form=self.attach_form,
            detach_form=self.detach_form,
            no_volumes_in_zone=len(self.attach_form.volume_id.choices) <= 1,
            instance_zone=self.instance.placement,
        )

    @view_config(route_name='instance_volumes', renderer=VIEW_TEMPLATE, request_method='GET')
    def instance_volumes(self):
        if self.instance is None:
            raise HTTPNotFound()
        render_dict = self.render_dict
        render_dict['volumes'] = self.get_attached_volumes()
        return render_dict

    @view_config(route_name='instance_volumes_json', renderer='json', request_method='GET')
    def instance_volumes_json(self):
        volumes = []
        transitional_states = ['creating', 'deleting', 'attaching', 'detaching']
        for volume in self.get_attached_volumes():
            status = volume.status
            attach_status = volume.attach_data.status
            is_transitional = status in transitional_states or attach_status in transitional_states
            detach_form_action = self.request.route_path(
                'instance_volume_detach', id=self.instance.id, volume_id=volume.id)
            volumes.append(dict(
                id=volume.id,
                name=TaggedItemView.get_display_name(volume),
                size=volume.size,
                device=volume.attach_data.device,
                attach_time=volume.attach_data.attach_time,
                status=status,
                attach_status=volume.attach_data.status,
                detach_form_action=detach_form_action,
                transitional=is_transitional,
            ))
        return dict(results=volumes)

    @view_config(route_name='instance_volume_attach', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_volume_attach(self):
        if self.attach_form.validate():
            volume_id = self.request.params.get('volume_id')
            device = self.request.params.get('device')
            if self.instance and volume_id and device:
                location = self.request.route_path('instance_volumes', id=self.instance.id)
                with boto_error_handler(self.request, location):
                    self.log_request(_(u"Attaching volume {0} to {1} as {2}").format(
                        volume_id, self.instance.id, device))
                    self.conn.attach_volume(volume_id=volume_id, instance_id=self.instance.id, device=device)
                    msg = _(u'Request successfully submitted.  It may take a moment to attach the volume.')
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                return HTTPFound(location=location)

    @view_config(route_name='instance_volume_detach', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_volume_detach(self):
        if self.detach_form.validate():
            volume_id = self.request.matchdict.get('volume_id')
            if volume_id:
                location = self.request.route_path('instance_volumes', id=self.instance.id)
                with boto_error_handler(self.request, location):
                    self.log_request(_(u"Dettaching volume {0} from {1}").format(volume_id, self.instance.id))
                    self.conn.detach_volume(volume_id=volume_id)
                    msg = _(u'Request successfully submitted.  It may take a moment to detach the volume.')
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                return HTTPFound(location=location)

    def get_attached_volumes(self):
        volumes = [vol for vol in self.volumes if vol.attach_data.instance_id == self.instance.id]
        # Sort by most recently attached first
        return sorted(volumes, key=attrgetter('attach_data.attach_time'), reverse=True) if volumes else []


class InstanceLaunchView(BlockDeviceMappingItemView):
    TEMPLATE = '../templates/instances/instance_launch.pt'

    def __init__(self, request):
        super(InstanceLaunchView, self).__init__(request)
        self.request = request
        self.image = self.get_image()
        self.location = self.request.route_path('instances')
        self.securitygroups = self.get_security_groups()
        self.iam_conn = self.get_connection(conn_type="iam")
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.launch_form = LaunchInstanceForm(
            self.request, image=self.image, securitygroups=self.securitygroups,
            conn=self.conn, vpc_conn=self.vpc_conn, iam_conn=self.iam_conn, formdata=self.request.params or None)
        self.filters_form = ImagesFiltersForm(
            self.request, cloud_type=self.cloud_type, formdata=self.request.params or None)
        self.keypair_form = KeyPairForm(self.request, formdata=self.request.params or None)
        self.securitygroup_form = SecurityGroupForm(self.request, self.vpc_conn, formdata=self.request.params or None)
        self.generate_file_form = GenerateFileForm(self.request, formdata=self.request.params or None)
        self.securitygroups_rules_json = BaseView.escape_json(json.dumps(self.get_securitygroups_rules()))
        self.images_json_endpoint = self.request.route_path('images_json')
        self.owner_choices = self.get_owner_choices()
        self.vpc_subnet_choices_json = BaseView.escape_json(json.dumps(self.get_vpc_subnets_json()))
        self.keypair_choices_json = BaseView.escape_json(json.dumps(dict(self.launch_form.keypair.choices)))
        self.securitygroup_choices_json = BaseView.escape_json(json.dumps(dict(self.launch_form.securitygroup.choices)))
        self.role_choices_json = BaseView.escape_json(json.dumps(dict(self.launch_form.role.choices)))
        self.render_dict = dict(
            image=self.image,
            launch_form=self.launch_form,
            filters_form=self.filters_form,
            keypair_form=self.keypair_form,
            securitygroup_form=self.securitygroup_form,
            generate_file_form=self.generate_file_form,
            images_json_endpoint=self.images_json_endpoint,
            owner_choices=self.owner_choices,
            snapshot_choices=self.get_snapshot_choices(),
            securitygroups_rules_json=self.securitygroups_rules_json,
            keypair_choices_json=self.keypair_choices_json,
            securitygroup_choices_json=self.securitygroup_choices_json,
            vpc_subnet_choices_json=self.vpc_subnet_choices_json,
            role_choices_json=self.role_choices_json,
            security_group_placeholder_text=_(u'Select...'),
        )

    @view_config(route_name='instance_create', renderer=TEMPLATE, request_method='GET')
    def instance_create(self):
        """Displays the Launch Instance wizard"""
        return self.render_dict

    @view_config(route_name='instance_launch', renderer=TEMPLATE, request_method='POST')
    def instance_launch(self):
        """Handles the POST from the Launch instanced wizard"""
        if self.launch_form.validate():
            tags_json = self.request.params.get('tags')
            image_id = self.image.id
            num_instances = int(self.request.params.get('number', 1))
            key_name = self.unescape_braces(self.request.params.get('keypair', ''))
            if key_name:
                # Handle "None (advanced)" option if key_name is 'none'
                key_name = None if key_name == 'none' else self.unescape_braces(key_name)
            securitygroup_ids = self.request.params.getall('securitygroup')
            instance_type = self.request.params.get('instance_type', 'm1.small')
            availability_zone = self.request.params.get('zone') or None
            vpc_network = self.request.params.get('vpc_network') or None
            vpc_subnet = self.request.params.get('vpc_subnet') or None
            associate_public_ip_address = self.request.params.get('associate_public_ip_address')
            if associate_public_ip_address == 'true':
                associate_public_ip_address = True
            elif associate_public_ip_address == 'false':
                associate_public_ip_address = False
            kernel_id = self.request.params.get('kernel_id') or None
            ramdisk_id = self.request.params.get('ramdisk_id') or None
            monitoring_enabled = self.request.params.get('monitoring_enabled') == 'y'
            private_addressing = self.request.params.get('private_addressing') == 'y'
            addressing_type = 'private' if private_addressing else 'public'
            bdmapping_json = self.request.params.get('block_device_mapping')
            block_device_map = self.get_block_device_map(bdmapping_json)
            role = self.request.params.get('role')
            new_instance_ids = []
            with boto_error_handler(self.request, self.location):
                instance_profile = None
                if role != '':  # need to set up instance profile, add role and supply to run_instances
                    instance_profile = RoleView.get_or_create_instance_profile(self.iam_conn, role)
                self.log_request(_(u"Running instance(s) (num={0}, image={1}, type={2})").format(
                    num_instances, image_id, instance_type))
                # Create base params for run_instances()
                params = dict(
                    min_count=num_instances,
                    max_count=num_instances,
                    key_name=key_name,
                    user_data=self.get_user_data(),
                    addressing_type=addressing_type,
                    instance_type=instance_type,
                    kernel_id=kernel_id,
                    ramdisk_id=ramdisk_id,
                    monitoring_enabled=monitoring_enabled,
                    block_device_map=block_device_map,
                    instance_profile_arn=instance_profile.arn if instance_profile else None,
                )
                if vpc_network is not None:
                    network_interface = NetworkInterfaceSpecification(
                        subnet_id=vpc_subnet,
                        groups=securitygroup_ids,
                        associate_public_ip_address=associate_public_ip_address,
                    )
                    network_interfaces = NetworkInterfaceCollection(network_interface)
                    # Specify VPC setting for the instances
                    params.update(dict(
                        network_interfaces=network_interfaces,
                    ))
                    reservation = self.conn.run_instances(image_id, **params)
                else:
                    # Use the EC2-Classic setting
                    params.update(dict(
                        placement=availability_zone,
                        security_group_ids=securitygroup_ids,
                    ))
                    reservation = self.conn.run_instances(image_id, **params)

                for idx, instance in enumerate(reservation.instances):
                    # Add tags for newly launched instance(s)
                    # Try adding name tag (from collection of name input fields)
                    input_field_name = 'name_{0}'.format(idx)
                    name = self.request.params.get(input_field_name, '').strip()
                    new_instance_ids.append(name or instance.id)
                    if name:
                        instance.add_tag('Name', name)
                    if tags_json:
                        tags = json.loads(tags_json)
                        for tagname, tagvalue in tags.items():
                            instance.add_tag(tagname, tagvalue)
                msg = _(u'Successfully sent launch instances request.  It may take a moment to launch instances ')
                msg += ', '.join(new_instance_ids)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        else:
            self.request.error_messages = self.launch_form.get_errors_list()
        return self.render_dict

    def get_security_groups(self):
        if self.conn:
            with boto_error_handler(self.request, self.location):
                return self.conn.get_all_security_groups()
        return []

    def get_securitygroups_rules(self):
        rules_dict = {}
        for security_group in self.securitygroups:
            rules = SecurityGroupsView.get_rules(security_group.rules)
            if security_group.vpc_id is not None:
                rules_egress = SecurityGroupsView.get_rules(security_group.rules_egress, rule_type='outbound')
                rules = rules + rules_egress
            rules_dict[security_group.id] = rules
        return rules_dict

    def get_securitygroup_id(self, name, vpc_network=None):
        for security_group in self.securitygroups:
            if security_group.vpc_id == vpc_network and security_group.name == name:
                return security_group.id
        return None

    def get_vpc_subnets_json(self):
        subnets = []
        if self.vpc_conn:
            with boto_error_handler(self.request, self.location):
                vpc_subnets = self.vpc_conn.get_all_subnets()
                for vpc_subnet in vpc_subnets:
                    subnets.append(dict(
                        id=vpc_subnet.id,
                        vpc_id=vpc_subnet.vpc_id,
                        availability_zone=vpc_subnet.availability_zone,
                        state=vpc_subnet.state,
                        cidr_block=vpc_subnet.cidr_block,
                    ))
        return subnets


class InstanceLaunchMoreView(BaseInstanceView, BlockDeviceMappingItemView):
    """Launch more like this instance view"""
    TEMPLATE = '../templates/instances/instance_launch_more.pt'

    def __init__(self, request):
        super(InstanceLaunchMoreView, self).__init__(request)
        self.request = request
        self.iam_conn = self.get_connection(conn_type="iam")
        self.instance = self.get_instance()
        self.instance_name = TaggedItemView.get_display_name(self.instance)
        self.image = self.get_image(instance=self.instance)  # From BaseInstanceView
        self.location = self.request.route_path('instances')
        self.launch_more_form = LaunchMoreInstancesForm(
            self.request, image=self.image, instance=self.instance,
            conn=self.conn, formdata=self.request.params or None)
        self.role = None
        self.associate_public_ip_address = 'Disabled'
        if self.instance.interfaces:
            if self.instance.interfaces[0] and hasattr(self.instance.interfaces[0], 'association'):
                self.associate_public_ip_address = 'Enabled'
        if self.instance.instance_profile:
            arn = self.instance.instance_profile['arn']
            profile_name = arn[(arn.rindex('/')+1):]
            inst_profile = self.iam_conn.get_instance_profile(profile_name)
            self.role = inst_profile.roles.member.role_name
        self.render_dict = dict(
            image=self.image,
            instance=self.instance,
            instance_name=self.instance_name,
            associate_public_ip_address=self.associate_public_ip_address,
            launch_more_form=self.launch_more_form,
            snapshot_choices=self.get_snapshot_choices(),
            vpc_subnet_display=self.get_vpc_subnet_display(self.instance.subnet_id) if self.instance else None,
            role=self.role,
        )

    @view_config(route_name='instance_more', renderer=TEMPLATE, request_method='GET')
    def instance_more(self):
        return self.render_dict

    @view_config(route_name='instance_more_launch', renderer=TEMPLATE, request_method='POST')
    def instance_more_launch(self):
        """Handles the POST from the Launch more instances like this form"""
        if self.launch_more_form.validate():
            image_id = self.image.id
            source_instance_tags = self.instance.tags
            key_name = self.instance.key_name
            num_instances = int(self.request.params.get('number', 1))
            security_groups = [group.id for group in self.instance.groups]
            instance_type = self.instance.instance_type
            availability_zone = self.instance.placement
            vpc_network = self.instance.vpc_id or None
            vpc_subnet = self.instance.subnet_id or None
            if self.associate_public_ip_address == 'Enabled':
                associate_public_ip_address = True
            else:
                associate_public_ip_address = False
            kernel_id = self.request.params.get('kernel_id') or None
            ramdisk_id = self.request.params.get('ramdisk_id') or None
            monitoring_enabled = self.request.params.get('monitoring_enabled') == 'y'
            private_addressing = self.request.params.get('private_addressing') == 'y'
            addressing_type = 'private' if private_addressing else 'public'
            bdmapping_json = self.request.params.get('block_device_mapping')
            block_device_map = self.get_block_device_map(bdmapping_json)
            new_instance_ids = []
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Running instance(s) (num={0}, image={1}, type={2})").format(
                    num_instances, image_id, instance_type))
                instance_profile_arn = self.instance.instance_profile['arn'] if self.instance.instance_profile else None
                # Create base params for run_instances()
                params = dict(
                    min_count=num_instances,
                    max_count=num_instances,
                    key_name=key_name,
                    user_data=self.get_user_data(),
                    addressing_type=addressing_type,
                    instance_type=instance_type,
                    kernel_id=kernel_id,
                    ramdisk_id=ramdisk_id,
                    monitoring_enabled=monitoring_enabled,
                    block_device_map=block_device_map,
                    instance_profile_arn=instance_profile_arn,
                )
                if vpc_network is not None:
                    network_interface = NetworkInterfaceSpecification(
                        subnet_id=vpc_subnet,
                        groups=security_groups,
                        associate_public_ip_address=associate_public_ip_address,
                    )
                    network_interfaces = NetworkInterfaceCollection(network_interface)
                    # Use the EC2-VPC setting
                    params.update(dict(
                        network_interfaces=network_interfaces,
                    ))
                    reservation = self.conn.run_instances(image_id, **params)
                else:
                    # Use the EC2-Classic setting
                    params.update(dict(
                        placement=availability_zone,
                        security_group_ids=security_groups,
                    ))
                    reservation = self.conn.run_instances(image_id, **params)

                for idx, instance in enumerate(reservation.instances):
                    # Add tags for newly launched instance(s)
                    # Try adding name tag (from collection of name input fields)
                    input_field_name = 'name_{0}'.format(idx)
                    name = self.request.params.get(input_field_name, '').strip()
                    new_instance_ids.append(name or instance.id)
                    if name:
                        instance.add_tag('Name', name)
                    if source_instance_tags:
                        for tagname, tagvalue in source_instance_tags.items():
                            # Don't copy 'Name' tag, and avoid tags that start with 'aws:' and 'euca:'
                            if all([tagname != 'Name', not tagname.startswith('aws:'),
                                    not tagname.startswith('euca:')]):
                                instance.add_tag(tagname, tagvalue)
                msg = _(u'Successfully sent launch instances request.  It may take a moment to launch instances ')
                msg += ', '.join(new_instance_ids)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        else:
            self.request.error_messages = self.launch_more_form.get_errors_list()
        return self.render_dict


class InstanceCreateImageView(BaseInstanceView, BlockDeviceMappingItemView):
    """Create image from an instance view"""
    TEMPLATE = '../templates/instances/instance_create_image.pt'

    def __init__(self, request):
        super(InstanceCreateImageView, self).__init__(request)
        self.request = request
        self.ec2_conn = self.get_connection()
        self.s3_conn = self.get_connection(conn_type='s3')
        self.instance = self.get_instance()
        self.instance_name = TaggedItemView.get_display_name(self.instance)
        self.location = self.request.route_path('instances')
        self.image = self.get_image(instance=self.instance)  # From BaseInstanceView
        self.create_image_form = InstanceCreateImageForm(
            self.request, instance=self.instance, ec2_conn=self.ec2_conn, s3_conn=self.s3_conn,
            formdata=self.request.params or None)
        image_id = _(u"missing")
        if self.image is not None:
            image_id = self.image.id
        self.create_image_form.description.data = _(u"created from instance {0} running image {1}").format(
            self.instance_name, image_id)
        self.render_dict = dict(
            instance=self.instance,
            instance_name=self.instance_name,
            image=self.image,
            snapshot_choices=self.get_snapshot_choices(),
            create_image_form=self.create_image_form,
        )

    @view_config(route_name='instance_create_image', renderer=TEMPLATE, request_method='GET')
    def instance_create_image_view(self):
        return self.render_dict

    @view_config(route_name='instance_create_image', renderer=TEMPLATE, request_method='POST')
    def instance_create_image_post(self):
        """Handles the POST from the create image from instance form"""
        is_ebs = True if self.instance.root_device_type == 'ebs' else False
        if is_ebs:  # remove fields not needed so validation passes
            del self.create_image_form.s3_bucket
            del self.create_image_form.s3_prefix
        else:
            del self.create_image_form.no_reboot
            # add selected bucket in case it's a new one
            s3_bucket = self.request.params.get('s3_bucket')
            if s3_bucket:
                s3_bucket = self.unescape_braces(s3_bucket)
            self.create_image_form.s3_bucket.choices.append((s3_bucket, s3_bucket))
        if self.create_image_form.validate():
            instance_id = self.instance.id
            name = self.request.params.get('name')
            description = self.request.params.get('description')
            tags_json = self.request.params.get('tags')
            bdm_json = self.request.params.get('block_device_mapping')
            if not is_ebs:
                s3_bucket = self.request.params.get('s3_bucket')
                if s3_bucket:
                    s3_bucket = self.unescape_braces(s3_bucket)
                s3_prefix = self.request.params.get('s3_prefix', '')
                with boto_error_handler(self.request, self.location):
                    self.log_request(_(u"Bundling instance {0}").format(instance_id))
                    account = self.request.session['account']
                    username = self.request.session['username']
                    password = self.request.params.get('password')
                    auth = self.get_euca_authenticator()
                    creds = auth.authenticate(
                        account=account, user=username, passwd=password,
                        timeout=8, duration=86400)  # 24 hours
                    upload_policy = BaseView.generate_default_policy(s3_bucket, s3_prefix, token=creds.session_token)
                    # we need to make the call ourselves to override boto's auto-signing
                    params = {
                        'InstanceId': instance_id,
                        'Storage.S3.Bucket': s3_bucket,
                        'Storage.S3.Prefix': s3_prefix,
                        'Storage.S3.UploadPolicy': upload_policy,
                        'Storage.S3.AWSAccessKeyId': creds.access_key,
                        'Storage.S3.UploadPolicySignature': BaseView.gen_policy_signature(
                            upload_policy, creds.secret_key)
                    }
                    result = self.conn.get_object('BundleInstance', params, BundleInstanceTask, verb='POST')
                    bundle_metadata = {
                        'version': curr_version,
                        'name': name,
                        'description': description,
                        'prefix': s3_prefix,
                        'virt_type': self.instance.virtualization_type,
                        'arch': self.instance.architecture,
                        'platform': self.instance.platform,
                        'kernel_id': self.instance.kernel,
                        'ramdisk_id': self.instance.ramdisk,
                        'bdm': bdm_json,
                        'tags': tags_json,
                        'bundle_id': result.id,
                    }
                    self.ec2_conn.create_tags(instance_id, {'ec_bundling': '%s/%s' % (s3_bucket, result.id)})
                    s3_conn = self.get_connection(conn_type='s3')
                    k = Key(s3_conn.get_bucket(s3_bucket))
                    k.key = result.id
                    k.set_contents_from_string(json.dumps(bundle_metadata))
                    msg = _(u'Successfully sent create image request.  It may take a few minutes to create the image.')
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                    return HTTPFound(location=self.request.route_path('image_view', id='p'+instance_id))
            else:
                no_reboot = self.request.params.get('no_reboot')
                with boto_error_handler(self.request, self.location):
                    self.log_request(_(u"Creating image from instance {0}").format(instance_id))
                    bdm = self.get_block_device_map(bdm_json)
                    if bdm.get(self.instance.root_device_name) is not None:
                        del bdm[self.instance.root_device_name]
                    image_id = self.ec2_conn.create_image(
                        instance_id, name, description=description, no_reboot=no_reboot, block_device_mapping=bdm)
                    tags = json.loads(tags_json)
                    self.ec2_conn.create_tags(image_id, tags)
                    msg = _(u'Successfully sent create image request.  It may take a few minutes to create the image.')
                    self.invalidate_images_cache()
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                    return HTTPFound(location=self.request.route_path('image_view', id=image_id))
        else:
            self.request.error_messages = self.create_image_form.get_errors_list()
        return self.render_dict


class InstanceTypesView(LandingPageView, BaseInstanceView):

    def __init__(self, request):
        super(InstanceTypesView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.render_dict = dict(
            instance_type_form=InstanceTypeForm(self.request),
            filter_fields=True,
            sort_keys=[],
            filter_keys=[],
            prefix='',
        )

    @view_config(route_name='instance_types', renderer='../templates/instances/instance_types.pt')
    def instance_types_landing(self):
        return self.render_dict

    @view_config(route_name='instance_types_json', renderer='json', request_method='POST')
    def instance_types_json(self):
        if not(self.request.session['account_access']):
            return JSONResponse(status=401, message=_(u"Unauthorized"))
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        instance_types_results = []
        with boto_error_handler(self.request):
            instance_types = self.conn.get_all_instance_types()
            for instance_type in instance_types:
                instance_types_results.append(dict(
                    name=instance_type.name,
                    cpu=instance_type.cores,
                    memory=instance_type.memory,
                    disk=instance_type.disk,
                ))
        return dict(results=instance_types_results)

    @view_config(route_name='instance_types_update', renderer='json', request_method='POST')
    def instance_types_update(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        # Extract the list of instance type updates
        update = {}
        for param in self.request.params.items():
            match = re.search('update\[(\d+)\]\[(\w+)\]', param[0])
            if match:
                index = match.group(1)
                attr = match.group(2)
                value = param[1]
                instance_type = {}
                if index in update:
                    instance_type = update[index]
                instance_type[attr] = value
                update[index] = instance_type
        # Modify instance type
        for item in update.itervalues():
            is_updated = self.modify_instance_type_attribute(
                item['name'], item['cpu'], item['memory'], item['disk'])
            if not is_updated:
                return JSONResponse(status=400, message=_(u"Failed to instance type attributes"))
        return dict(message=_(u"Successfully updated instance type attributes"))

    def modify_instance_type_attribute(self, name, cpu, memory, disk):
        # Ensure that the attributes are positive integers
        if cpu <= 0 or memory <= 0 or disk <= 0:
            return False
        params = {'Name': name, 'Cpu': cpu, 'Memory': memory, 'Disk': disk}
        with boto_error_handler(self.request):
            return self.conn.get_status('ModifyInstanceTypeAttribute', params, verb='POST')
