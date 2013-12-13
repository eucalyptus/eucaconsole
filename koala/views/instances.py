# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS instances

"""
from dateutil import parser
from operator import attrgetter
import time

from boto.exception import EC2ResponseError

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.instances import InstanceForm, AttachVolumeForm, DetachVolumeForm
from ..forms.instances import RebootInstanceForm, StartInstanceForm, StopInstanceForm, TerminateInstanceForm
from ..models import LandingPageFilter, Notification
from ..views import BaseView, LandingPageView, TaggedItemView


class InstancesView(LandingPageView):
    def __init__(self, request):
        super(InstancesView, self).__init__(request)
        self.conn = self.get_connection()
        self.items = self.get_items()
        self.initial_sort_key = '-launch_time'
        self.prefix = '/instances'
        self.filter_fields = self.get_filter_fields()
        self.json_items_endpoint = self.get_json_endpoint('instances_json')
        self.render_dict = dict(
            display_type=self.display_type,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
        )

    def get_items(self):
        return self.conn.get_only_instances() if self.conn else []

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt')
    def instances_landing(self):
        filter_keys = [
            'id', 'instance_type', 'ip_address', 'key_name', 'placement',
            'root_device', 'security_groups', 'state', 'tags']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='-launch_time', name=_(u'Launch time (most recent first)')),
            dict(key='id', name=_(u'Instance ID')),
            dict(key='placement', name=_(u'Availability zone')),
            dict(key='root_device', name=_(u'Root device')),
            dict(key='key_name', name=_(u'Key pair')),
        ]
        self.render_dict.update(dict(
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            json_items_endpoint=self.json_items_endpoint,
        ))
        return self.render_dict

    @view_config(route_name='instances_json', renderer='json', request_method='GET')
    def instances_json(self):
        instances = []
        filtered_items = self.filter_items(self.items)
        for instance in filtered_items:
            instances.append(dict(
                id=instance.id,
                instance_type=instance.instance_type,
                ip_address=instance.ip_address,
                launch_time=instance.launch_time,
                placement=instance.placement,
                root_device=instance.root_device_type,
                security_groups=', '.join(group.name for group in instance.groups),
                key_name=instance.key_name,
                status=instance.state,
                tags=TaggedItemView.get_tags_display(instance.tags)
            ))
        return dict(results=instances)

    def get_filter_fields(self):
        """Filter fields are passed to 'properties_filter_form' template macro to display filters at left"""
        status_choices = sorted(set(instance.state for instance in self.items))
        instance_type_choices = sorted(set(instance.instance_type for instance in self.items))
        avail_zone_choices = sorted(set(instance.placement for instance in self.items))
        return [
            LandingPageFilter(key='state', name=_(u'Status'), choices=status_choices),
            LandingPageFilter(key='instance_type', name=_(u'Instance type'), choices=instance_type_choices),
            LandingPageFilter(key='placement', name=_(u'Availability zone'), choices=avail_zone_choices),
        ]


class InstanceView(TaggedItemView):
    VIEW_TEMPLATE = '../templates/instances/instance_view.pt'

    def __init__(self, request):
        super(InstanceView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.instance = self.get_instance()
        self.image = self.get_image()
        self.scaling_group = self.get_scaling_group()
        self.instance_form = InstanceForm(
            self.request, instance=self.instance, conn=self.conn, formdata=self.request.params or None)
        self.reboot_form = RebootInstanceForm(self.request, formdata=self.request.params or None)
        self.start_form = StartInstanceForm(self.request, formdata=self.request.params or None)
        self.stop_form = StopInstanceForm(self.request, formdata=self.request.params or None)
        self.terminate_form = TerminateInstanceForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.instance
        self.launch_time = self.get_launch_time()
        self.name_tag = self.instance.tags.get('Name', '') if self.instance else None
        self.instance_name = '{}{}'.format(
            self.instance.id, ' ({})'.format(self.name_tag) if self.name_tag else '') if self.instance else ''
        self.render_dict = dict(
            instance=self.instance,
            instance_name=self.instance_name,
            image=self.image,
            scaling_group=self.scaling_group,
            instance_form=self.instance_form,
            instance_launch_time=self.launch_time,
            reboot_form=self.reboot_form,
            start_form=self.start_form,
            stop_form=self.stop_form,
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
            # Update tags
            self.update_tags()

            # Update assigned IP address
            new_ip = self.request.params.get('ip_address')
            if new_ip and new_ip != self.instance.ip_address:
                self.instance.use_ip(new_ip)
                time.sleep(1)  # Give backend time to allocate IP address

            # Disassociate IP address
            if new_ip == '':
                self.disassociate_ip_address(ip_address=self.instance.ip_address)

            location = self.request.route_url('instance_view', id=self.instance.id)
            msg = _(u'Successfully modified instance')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='instance_launch', renderer='../templates/instances/instance_launch.pt')
    def instance_launch(self):
        # TODO: Implement
        image_id = self.request.params.get('image_id')
        image = self.conn.get_image(image_id)
        return dict(
            image=image
        )

    @view_config(route_name='instance_reboot', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_reboot(self):
        if self.instance and self.reboot_form.validate():
            rebooted = self.instance.reboot()
            time.sleep(1)
            location = self.request.route_url('instance_view', id=self.instance.id)
            msg = _(u'Successfully sent reboot request.  It may take a moment to reboot the instance.')
            queue = Notification.SUCCESS
            if not rebooted:
                msg = _(u'Unable to reboot the instance.')
                queue = Notification.ERROR
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='instance_stop', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_stop(self):
        if self.instance and self.stop_form.validate():
            # Only EBS-backed instances can be stopped
            if self.image.root_device_type == 'ebs':
                self.instance.stop()
                location = self.request.route_url('instance_view', id=self.instance.id)
                msg = _(u'Successfully sent stop instance request.  It may take a moment to stop the instance.')
                queue = Notification.SUCCESS
                self.request.session.flash(msg, queue=queue)
                return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='instance_start', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_start(self):
        if self.instance and self.start_form.validate():
            # Can only start an instance if it has a volume attached
            self.instance.start()
            location = self.request.route_url('instance_view', id=self.instance.id)
            msg = _(u'Successfully sent start instance request.  It may take a moment to start the instance.')
            queue = Notification.SUCCESS
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='instance_terminate', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_terminate(self):
        if self.instance and self.terminate_form.validate():
            self.instance.terminate()
            time.sleep(1)
            location = self.request.route_url('instance_view', id=self.instance.id)
            msg = _(u'Successfully sent terminate instance request.  It may take a moment to shut down the instance.')
            queue = Notification.SUCCESS
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    def get_instance(self):
        instance_id = self.request.matchdict.get('id')
        if instance_id:
            instances_list = self.conn.get_only_instances(instance_ids=[instance_id])
            return instances_list[0] if instances_list else None
        return None

    def get_launch_time(self):
        """Returns instance launch time as a python datetime.datetime object"""
        if self.instance and self.instance.launch_time:
            return parser.parse(self.instance.launch_time)
        return None

    def get_image(self):
        if self.instance:
            return self.conn.get_image(self.instance.image_id)
        return None

    def get_scaling_group(self):
        if self.instance:
            return self.instance.tags.get('aws:autoscaling:groupName')
        return None

    def disassociate_ip_address(self, ip_address=None):
        ip_addresses = self.conn.get_all_addresses(addresses=[ip_address])
        elastic_ip = ip_addresses[0] if ip_addresses else None
        if elastic_ip:
            disassociated = elastic_ip.disassociate()
            if disassociated:
                time.sleep(1)  # Give backend time to disassociate IP address


class InstanceStateView(BaseView):
    def __init__(self, request):
        super(InstanceStateView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.instance = self.get_instance()

    @view_config(route_name='instance_state_json', renderer='json', request_method='GET')
    def instance_state_json(self):
        """Return current instance state"""
        return dict(results=self.instance.state)

    def get_instance(self):
        instance_id = self.request.matchdict.get('id')
        if instance_id:
            instances_list = self.conn.get_only_instances(instance_ids=[instance_id])
            return instances_list[0] if instances_list else None
        return None


class InstanceVolumesView(BaseView):
    VIEW_TEMPLATE = '../templates/instances/instance_volumes.pt'

    def __init__(self, request):
        super(InstanceVolumesView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.instance = self.get_instance()
        self.attach_form = AttachVolumeForm(
            self.request, conn=self.conn, instance=self.instance, formdata=self.request.params or None)
        self.inst_name_tag = self.instance.tags.get('Name', '') if self.instance else None
        self.instance_name = '{}{}'.format(
            self.instance.id, ' ({})'.format(self.inst_name_tag) if self.inst_name_tag else '') if self.instance else ''
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
            detach_form_action = self.request.route_url(
                'instance_volume_detach', id=self.instance.id, volume_id=volume.id)
            volumes.append(dict(
                id=volume.id,
                name=volume.tags.get('Name', ''),
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
            volume = None
            if volume_id:
                volume_ids = [volume_id]
                volumes = self.conn.get_all_volumes(volume_ids=volume_ids)
                volume = volumes[0] if volumes else None
            if self.instance and volume and device:
                location = self.request.route_url('instance_volumes', id=self.instance.id)
                try:
                    volume.attach(self.instance.id, device)
                    msg = _(u'Request successfully submitted.  It may take a moment to attach the volume.')
                    queue = Notification.SUCCESS
                    time.sleep(1)
                except EC2ResponseError as err:
                    msg = err.message
                    queue = Notification.ERROR
                self.request.session.flash(msg, queue=queue)
                return HTTPFound(location=location)

    @view_config(route_name='instance_volume_detach', renderer=VIEW_TEMPLATE, request_method='POST')
    def instance_volume_detach(self):
        if self.detach_form.validate():
            volume_id = self.request.matchdict.get('volume_id')
            volume = None
            if volume_id:
                volume_ids = [volume_id]
                volumes = self.conn.get_all_volumes(volume_ids=volume_ids)
                volume = volumes[0] if volumes else None
            if volume:
                volume.detach()
                time.sleep(1)
                location = self.request.route_url('instance_volumes', id=self.instance.id)
                msg = _(u'Request successfully submitted.  It may take a moment to detach the volume.')
                queue = Notification.SUCCESS
                self.request.session.flash(msg, queue=queue)
                return HTTPFound(location=location)

    def get_instance(self):
        instance_id = self.request.matchdict.get('id')
        if instance_id:
            instances_list = self.conn.get_only_instances(instance_ids=[instance_id])
            return instances_list[0] if instances_list else None
        return None

    def get_attached_volumes(self):
        volumes = [vol for vol in self.conn.get_all_volumes() if vol.attach_data.instance_id == self.instance.id]
        # Sort by most recently attached first
        return sorted(volumes, key=attrgetter('attach_data.attach_time'), reverse=True) if volumes else []

