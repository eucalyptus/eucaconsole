# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS instances

"""
from dateutil import parser
import time

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.instances import InstanceForm
from ..forms.instances import RebootInstanceForm, StartInstanceForm, StopInstanceForm, TerminateInstanceForm
from ..models import LandingPageFilter, Notification
from ..views import BaseView, LandingPageView, TaggedItemView


class InstancesView(LandingPageView):
    def __init__(self, request):
        super(InstancesView, self).__init__(request)
        self.items = self.get_items()
        self.initial_sort_key = '-launch_time'
        self.prefix = '/instances'

    def get_items(self):
        conn = self.get_connection()
        return conn.get_only_instances() if conn else []

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt')
    def instances_landing(self):
        json_items_endpoint = self.request.route_url('instances_json')
        status_choices = sorted(set(instance.state for instance in self.items))
        instance_type_choices = sorted(set(instance.instance_type for instance in self.items))
        avail_zone_choices = sorted(set(instance.placement for instance in self.items))
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        self.filter_fields = [
            LandingPageFilter(key='status', name=_(u'Status'), choices=status_choices),
            LandingPageFilter(key='instance_type', name=_(u'Instance type'), choices=instance_type_choices),
            LandingPageFilter(key='placement', name=_(u'Availability zone'), choices=avail_zone_choices),
        ]
        more_filter_keys = ['id', 'name', 'ip_address']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='-launch_time', name=_(u'Launch time (most recent first)')),
            dict(key='name', name=_(u'Instance name')),
        ]

        return dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
        )

    @view_config(route_name='instances_json', renderer='json', request_method='GET')
    def instances_json(self):
        instances = []
        for instance in self.items:
            instances.append(dict(
                id=instance.id,
                instance_type=instance.instance_type,
                ip_address=instance.ip_address,
                launch_time=instance.launch_time,
                placement=instance.placement,
                root_device=instance.root_device_name,
                security_groups=', '.join(group.name for group in instance.groups),
                key_name=instance.key_name,
                status=instance.state,
            ))
        return dict(results=instances)


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
        self.render_dict = dict(
            instance=self.instance,
            image=self.image,
            scaling_group=self.scaling_group,
            instance_form=self.instance_form,
            instance_launch_time=self.launch_time,
            reboot_form=self.reboot_form,
            start_form=self.start_form,
            stop_form=self.stop_form,
            terminate_form=self.terminate_form,
        )

    @view_config(route_name='instance_view', renderer=VIEW_TEMPLATE)
    def instance_view(self):
        if self.instance is None:
            raise HTTPNotFound()
        return self.render_dict

    @view_config(route_name='instance_update', renderer=VIEW_TEMPLATE)
    def instance_update(self):
        if self.instance is None:
            raise HTTPNotFound()
        if self.instance_form.validate():
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

    @view_config(route_name='instance_reboot', renderer=VIEW_TEMPLATE)
    def instance_reboot(self):
        if self.reboot_form.validate():
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

    @view_config(route_name='instance_stop', renderer=VIEW_TEMPLATE)
    def instance_stop(self):
        if self.stop_form.validate():
            # Only EBS-backed instances can be stopped
            if self.image.root_device_type == 'ebs':
                self.instance.stop()
                location = self.request.route_url('instance_view', id=self.instance.id)
                msg = _(u'Successfully sent stop instance request.  It may take a moment to stop the instance.')
                queue = Notification.SUCCESS
                self.request.session.flash(msg, queue=queue)
                return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='instance_start', renderer=VIEW_TEMPLATE)
    def instance_start(self):
        if self.start_form.validate():
            # Can only start an instance if it has a volume attached
            self.instance.start()
            location = self.request.route_url('instance_view', id=self.instance.id)
            msg = _(u'Successfully sent start instance request.  It may take a moment to start the instance.')
            queue = Notification.SUCCESS
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='instance_terminate', renderer=VIEW_TEMPLATE)
    def instance_terminate(self):
        if self.terminate_form.validate():
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
        if self.instance.launch_time:
            return parser.parse(self.instance.launch_time)
        return None

    def get_image(self):
        if self.instance is None:
            raise HTTPNotFound()
        return self.conn.get_image(self.instance.image_id)

    def get_scaling_group(self):
        return self.instance.tags.get('aws:autoscaling:groupName')

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

    @view_config(route_name='instance_state_json', renderer='json')
    def instance_state_json(self):
        """Return current instance state"""
        return dict(results=self.instance.state)

    def get_instance(self):
        instance_id = self.request.matchdict.get('id')
        if instance_id:
            instances_list = self.conn.get_only_instances(instance_ids=[instance_id])
            return instances_list[0] if instances_list else None
        return None
