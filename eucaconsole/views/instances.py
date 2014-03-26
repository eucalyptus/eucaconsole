# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS instances

"""
import base64
from dateutil import parser
from operator import attrgetter
import simplejson as json
from M2Crypto import RSA

from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.images import ImagesFiltersForm
from ..forms.instances import (
    InstanceForm, AttachVolumeForm, DetachVolumeForm, LaunchInstanceForm, LaunchMoreInstancesForm,
    RebootInstanceForm, StartInstanceForm, StopInstanceForm, TerminateInstanceForm,
    BatchTerminateInstancesForm, InstancesFiltersForm)
from ..forms import GenerateFileForm
from ..forms.keypairs import KeyPairForm
from ..forms.securitygroups import SecurityGroupForm
from ..models import Notification
from ..views import BaseView, LandingPageView, TaggedItemView, BlockDeviceMappingItemView, JSONResponse
from ..views.images import ImageView
from ..views.securitygroups import SecurityGroupsView
from . import boto_error_handler


class BaseInstanceView(BaseView):
    """Base class for instance-related views"""
    def __init__(self, request):
        super(BaseInstanceView, self).__init__(request)
        self.conn = self.get_connection()

    def get_instance(self, instance_id=None):
        instance_id = instance_id or self.request.matchdict.get('id')
        if instance_id:
            try:
                reservations_list = self.conn.get_all_reservations(instance_ids=[instance_id])
                reservation = reservations_list[0] if reservations_list else None
                if reservation:
                    instance = reservation.instances[0]
                    instance.groups = reservation.groups
                    instance.reservation_id = reservation.id
                    instance.owner_id = reservation.owner_id
                    if instance.platform is None:
                        instance.platform = _(u"linux")
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


class InstancesView(LandingPageView, BaseInstanceView):
    def __init__(self, request):
        super(InstancesView, self).__init__(request)
        self.initial_sort_key = '-launch_time'
        self.prefix = '/instances'
        self.filter_fields = True
        self.json_items_endpoint = self.get_json_endpoint('instances_json')
        self.location = self.get_redirect_location('instances')
        self.start_form = StartInstanceForm(self.request, formdata=self.request.params or None)
        self.stop_form = StopInstanceForm(self.request, formdata=self.request.params or None)
        self.reboot_form = RebootInstanceForm(self.request, formdata=self.request.params or None)
        self.terminate_form = TerminateInstanceForm(self.request, formdata=self.request.params or None)
        self.batch_terminate_form = BatchTerminateInstancesForm(self.request, formdata=self.request.params or None)
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.filters_form = InstancesFiltersForm(
            self.request, ec2_conn=self.conn, autoscale_conn=self.autoscale_conn,
            cloud_type=self.cloud_type, formdata=self.request.params or None)
        self.render_dict = dict(
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            start_form=self.start_form,
            stop_form=self.stop_form,
            reboot_form=self.reboot_form,
            terminate_form=self.terminate_form,
            batch_terminate_form=self.batch_terminate_form,
            filters_form=self.filters_form,
        )

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt')
    def instances_landing(self):
        filter_keys = [
            'id', 'name', 'image_id', 'instance_type', 'ip_address', 'key_name', 'placement',
            'root_device', 'security_groups_string', 'state', 'tags']
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
        self.render_dict.update(dict(
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            json_items_endpoint=self.json_items_endpoint,
        ))
        return self.render_dict

    @view_config(route_name='instances_start', request_method='POST')
    def instances_start(self):
        instance_id = self.request.params.get('instance_id')
        instance = self.get_instance(instance_id)
        if instance and self.start_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Starting instance {0}").format(instance_id))
                # Can only start an instance if it has a volume attached
                instance.start()
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
        instance_image = self.get_image(instance)
        if instance and self.stop_form.validate():
            # Only EBS-backed instances can be stopped
            if instance_image.root_device_type == 'ebs':
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
        instance = self.get_instance(instance_id)
        if instance and self.reboot_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Rebooting instance {0}").format(instance_id))
                rebooted = instance.reboot()
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
        # IMHO, this is goofy... instance_id is part of request path, don't need an additional parameter
        # and there is no reason to fetch the instance before terminating.. 1 extra CLC call
        instance_id = self.request.params.get('instance_id')
        instance = self.get_instance(instance_id)
        if instance and self.terminate_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Terminating instance {0}").format(instance_id))
                instance.terminate()
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


class InstancesJsonView(LandingPageView):
    def __init__(self, request):
        super(InstancesJsonView, self).__init__(request)
        self.conn = self.get_connection()

    @view_config(route_name='instances_json', renderer='json', request_method='GET')
    def instances_json(self):
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
            filters.update({'group-name': security_group_param})
        root_device_type_param = self.request.params.getall('root_device_type')
        if root_device_type_param:
            filters.update({'root-device-type': root_device_type_param})
        # Don't filter by these request params in Python, as they're included in the "filters" params sent to the CLC
        # Note: the choices are from attributes in InstancesFiltersForm
        ignore_params = [
            'availability_zone', 'instance_type', 'state', 'security_group', 'scaling_group', 'root_device_type']
        filtered_items = self.filter_items(self.get_items(filters=filters), ignore=ignore_params)
        if self.request.params.get('scaling_group'):
            filtered_items = self.filter_by_scaling_group(filtered_items)
        transitional_states = ['pending', 'stopping', 'shutting-down']
        for instance in filtered_items:
            is_transitional = instance.state in transitional_states
            security_groups_array = sorted({'name':group.name, 'id':group.id} for group in instance.groups)
            if instance.platform is None:
                instance.platform = _(u"linux")
            instances.append(dict(
                id=instance.id,
                name=TaggedItemView.get_display_name(instance),
                instance_type=instance.instance_type,
                image_id=instance.image_id,
                ip_address=instance.ip_address,
                public_dns_name=instance.public_dns_name,
                launch_time=instance.launch_time,
                placement=instance.placement,
                platform=instance.platform,
                root_device=instance.root_device_type,
                security_groups=security_groups_array,
                key_name=instance.key_name,
                status=instance.state,
                tags=TaggedItemView.get_tags_display(instance.tags),
                transitional=is_transitional,
            ))
        return dict(results=instances)

    def get_items(self, filters=None):
        if self.conn:
            instances = []
            with boto_error_handler(self.request):
                for reservation in self.conn.get_all_reservations(filters=filters):
                    for instance in reservation.instances:
                        instance.groups = reservation.groups
                        instances.append(instance)
            return instances
        return []

    def filter_by_scaling_group(self, items):
        filtered_items = []
        for item in items:
            autoscaling_tag = item.tags.get('aws:autoscaling:groupName')
            if autoscaling_tag:
                for scaling_group in self.request.params.getall('scaling_group'):
                    if autoscaling_tag == scaling_group:
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
        self.instance = self.get_instance()
        self.image = self.get_image(self.instance)
        self.scaling_group = self.get_scaling_group()
        self.instance_form = InstanceForm(
            self.request, instance=self.instance, conn=self.conn, formdata=self.request.params or None)
        self.start_form = StartInstanceForm(self.request, formdata=self.request.params or None)
        self.stop_form = StopInstanceForm(self.request, formdata=self.request.params or None)
        self.reboot_form = RebootInstanceForm(self.request, formdata=self.request.params or None)
        self.terminate_form = TerminateInstanceForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.instance
        self.launch_time = self.get_launch_time()
        self.location = self.get_redirect_location()
        self.instance_name = TaggedItemView.get_display_name(self.instance)
        self.render_dict = dict(
            instance=self.instance,
            instance_name=self.instance_name,
            image=self.image,
            scaling_group=self.scaling_group,
            instance_form=self.instance_form,
            instance_launch_time=self.launch_time,
            start_form=self.start_form,
            stop_form=self.stop_form,
            reboot_form=self.reboot_form,
            terminate_form=self.terminate_form,
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

                # Update assigned IP address
                new_ip = self.request.params.get('ip_address')
                if new_ip and new_ip != self.instance.ip_address and new_ip != 'none' and self.instance.state != 'stopped':
                    self.log_request(_(u"Associating eip {0} with instance {0}").format(new_ip, self.instance.id))
                    self.instance.use_ip(new_ip)

                # Disassociate IP address
                if new_ip == '':
                    self.log_request(_(u"Disassociating eip {0} with instance {0}").format(self.instance.ip_address, self.instance.id))
                    self.disassociate_ip_address(ip_address=self.instance.ip_address)

                # Update stopped instance
                if self.instance.state == 'stopped':
                    instance_type = self.request.params.get('instance_type')
                    user_data = self.request.params.get('userdata')
                    kernel = self.request.params.get('kernel')
                    ramdisk = self.request.params.get('ramdisk')
                    self.log_request(_(u"Updating instance {0} (type={1}, kernel={2}, ramidisk={3})").format(self.instance.id, instance_type, kernel, ramdisk))
                    self.instance.instance_type = instance_type
                    self.instance.user_data = user_data
                    self.instance.kernel = kernel
                    self.instance.ramdisk = ramdisk
                    self.instance.update()

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

    def get_launch_time(self):
        """Returns instance launch time as a python datetime.datetime object"""
        if self.instance and self.instance.launch_time:
            return parser.parse(self.instance.launch_time)
        return None

    def get_scaling_group(self):
        if self.instance:
            return self.instance.tags.get('aws:autoscaling:groupName')
        return None

    def get_redirect_location(self):
        if self.instance:
            return self.request.route_path('instance_view', id=self.instance.id)
        return ''

    def disassociate_ip_address(self, ip_address=None):
        ip_addresses = self.conn.get_all_addresses(addresses=[ip_address])
        elastic_ip = ip_addresses[0] if ip_addresses else None
        if elastic_ip:
            self.log_request(_(u"Disassociating ip {0} from instance {1}").format(ip_address, self.instance.id))
            disassociated = elastic_ip.disassociate()


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

    @view_config(route_name='instance_nextdevice_json', renderer='json', request_method='GET')
    def instance_nextdevice_json(self):
        """Return current instance state"""
        return dict(results=self.suggest_next_device_name(self.instance))

    @view_config(route_name='instance_console_output_json', renderer='json', request_method='GET')
    def instance_console_output_json(self):
        """Return console output for instance"""
        with boto_error_handler(self.request):
            output = self.conn.get_console_output(instance_id=self.instance.id)
        return dict(results=output.output)

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
                    self.log_request(_(u"Attaching volume {0} to {1} as {2}").format(volume_id, self.instance.id, device))
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
        self.launch_form = LaunchInstanceForm(
            self.request, image=self.image, securitygroups=self.securitygroups,
            conn=self.conn, formdata=self.request.params or None)
        self.filters_form = ImagesFiltersForm(
            self.request, cloud_type=self.cloud_type, formdata=self.request.params or None)
        self.keypair_form = KeyPairForm(self.request, formdata=self.request.params or None)
        self.securitygroup_form = SecurityGroupForm(self.request, formdata=self.request.params or None)
        self.generate_file_form = GenerateFileForm(self.request, formdata=self.request.params or None)
        self.securitygroups_rules_json = json.dumps(self.get_securitygroups_rules())
        self.images_json_endpoint = self.request.route_path('images_json')
        self.owner_choices = self.get_owner_choices()
        self.keypair_choices_json = json.dumps(dict(self.launch_form.keypair.choices))
        self.securitygroup_choices_json = json.dumps(dict(self.launch_form.securitygroup.choices))
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
            security_group_names=[name for name, label in self.launch_form.securitygroup.choices],
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
            key_name = self.request.params.get('keypair')
            if key_name and key_name == 'none':
                key_name = None  # Handle "None (advanced)" option
            num_instances = int(self.request.params.get('number', 1))
            securitygroup = self.request.params.get('securitygroup', 'default')
            security_groups = [securitygroup]  # Security group names
            instance_type = self.request.params.get('instance_type', 'm1.small')
            availability_zone = self.request.params.get('zone') or None
            kernel_id = self.request.params.get('kernel_id') or None
            ramdisk_id = self.request.params.get('ramdisk_id') or None
            monitoring_enabled = self.request.params.get('monitoring_enabled', False)
            private_addressing = self.request.params.get('private_addressing', False)
            addressing_type = 'private' if private_addressing else 'public'
            bdmapping_json = self.request.params.get('block_device_mapping')
            block_device_map = self.get_block_device_map(bdmapping_json)
            new_instance_ids = []
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Running instance(s) (num={0}, image={1}, type={2})").format(num_instances, image_id, instance_type))
                reservation = self.conn.run_instances(
                    image_id,
                    max_count=num_instances,
                    key_name=key_name,
                    user_data=self.get_user_data(),
                    addressing_type=addressing_type,
                    instance_type=instance_type,
                    placement=availability_zone,
                    kernel_id=kernel_id,
                    ramdisk_id=ramdisk_id,
                    monitoring_enabled=monitoring_enabled,
                    block_device_map=block_device_map,
                    security_group_ids=security_groups,
                )
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
        return self.render_dict

    def get_security_groups(self):
        if self.conn:
            with boto_error_handler(self.request, self.location):
                return self.conn.get_all_security_groups()
        return []

    def get_securitygroups_rules(self):
        rules_dict = {}
        for security_group in self.securitygroups:
            rules_dict[security_group.name] = SecurityGroupsView.get_rules(security_group.rules)
        return rules_dict


class InstanceLaunchMoreView(BaseInstanceView, BlockDeviceMappingItemView):
    """Launch more like this instance view"""
    TEMPLATE = '../templates/instances/instance_launch_more.pt'

    def __init__(self, request):
        super(InstanceLaunchMoreView, self).__init__(request)
        self.request = request
        self.instance = self.get_instance()
        self.instance_name = TaggedItemView.get_display_name(self.instance)
        self.image = self.get_image(instance=self.instance)  # From BaseInstanceView
        self.location = self.request.route_path('instances')
        self.launch_more_form = LaunchMoreInstancesForm(
            self.request, image=self.image, conn=self.conn, formdata=self.request.params or None)
        self.render_dict = dict(
            image=self.image,
            instance=self.instance,
            instance_name=self.instance_name,
            launch_more_form=self.launch_more_form,
            snapshot_choices=self.get_snapshot_choices(),
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
            security_groups = [group.name for group in self.instance.groups]
            instance_type = self.instance.instance_type
            availability_zone = self.instance.placement
            kernel_id = self.request.params.get('kernel_id') or None
            ramdisk_id = self.request.params.get('ramdisk_id') or None
            monitoring_enabled = self.request.params.get('monitoring_enabled', False)
            private_addressing = self.request.params.get('private_addressing', False)
            addressing_type = 'private' if private_addressing else 'public'
            bdmapping_json = self.request.params.get('block_device_mapping')
            block_device_map = self.get_block_device_map(bdmapping_json)
            new_instance_ids = []
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Running instance(s) (num={0}, image={1}, type={2})").format(num_instances, image_id, instance_type))
                reservation = self.conn.run_instances(
                    image_id,
                    max_count=num_instances,
                    key_name=key_name,
                    user_data=self.get_user_data(),
                    addressing_type=addressing_type,
                    instance_type=instance_type,
                    placement=availability_zone,
                    kernel_id=kernel_id,
                    ramdisk_id=ramdisk_id,
                    monitoring_enabled=monitoring_enabled,
                    block_device_map=block_device_map,
                    security_group_ids=security_groups,
                )
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
                            # Don't copy 'Name' tag, and avoid tags that start with 'aws:'
                            if all([tagname != 'Name', not tagname.startswith('aws:')]):
                                instance.add_tag(tagname, tagvalue)
                msg = _(u'Successfully sent launch instances request.  It may take a moment to launch instances ')
                msg += ', '.join(new_instance_ids)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        else:
            self.request.error_messages = self.launch_more_form.get_errors_list()
        return self.render_dict
