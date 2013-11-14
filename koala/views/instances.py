# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS instances

"""
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..views import LandingPageView


class InstancesView(LandingPageView):
    def __init__(self, request):
        super(InstancesView, self).__init__(request)
        self.items = self.get_items()
        self.initial_sort_key = '-launch_time'
        self.prefix = '/instances'

    def get_items(self):
        conn = self.get_connection()
        return conn.get_only_instances()

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt')
    def instances_landing(self):
        json_items_endpoint = self.request.route_url('instances_json')
        state_choices = sorted(set(instance.state for instance in self.items))
        root_device_type_choices = ('ebs', 'instance-store')
        instance_type_choices = sorted(set(instance.instance_type for instance in self.items))
        avail_zone_choices = sorted(set(instance.placement for instance in self.items))
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        self.filter_fields = [
            LandingPageFilter(key='state', name='Status', choices=state_choices),
            LandingPageFilter(key='root_device_type', name='Root device', choices=root_device_type_choices),
            LandingPageFilter(key='instance_type', name='Instance type', choices=instance_type_choices),
            LandingPageFilter(key='placement', name='Availability zone', choices=avail_zone_choices),
        ]
        more_filter_keys = ['id', 'name']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='-launch_time', name='Launch time (most recent first)'),
            dict(key='name', name='Instance name'),
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
                state=instance.state,
            ))
        return dict(results=instances)


class InstanceView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='instance_view', renderer='../templates/instances/instance_view.pt')
    def instance_view(self):
        instance_id = self.request.matchdict.get('id')
        return dict(instance_id=instance_id)
