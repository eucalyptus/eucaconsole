# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS scaling groups

"""
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..views import LandingPageView


class ScalingGroupsView(LandingPageView):
    def __init__(self, request):
        super(ScalingGroupsView, self).__init__(request)
        self.items = self.get_items()
        self.initial_sort_key = 'name'
        self.prefix = '/scalinggroups'

    def get_items(self):
        conn = self.get_connection(conn_type='autoscale')
        return conn.get_all_groups()

    @view_config(route_name='scalinggroups', renderer='../templates/scalinggroups/scalinggroups.pt')
    def scalinggroups_landing(self):
        json_items_endpoint = self.request.route_url('scalinggroups_json')
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        launch_config_choices = sorted(set(item.launch_config for item in self.items))
        self.filter_fields = [
            LandingPageFilter(key='launch_config', name='Launch Configuration', choices=launch_config_choices),
        ]
        more_filter_keys = ['availability_zones', 'name', 'placement_group']
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name='Name'),
            dict(key='launch_config', name='Launch configuration'),
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

    @view_config(route_name='scalinggroups_json', renderer='json', request_method='GET')
    def scalinggroups_json(self):
        scalinggroups = []
        for group in self.items:
            scalinggroups.append(dict(
                availability_zones=', '.join(group.availability_zones),
                desired_capacity=group.desired_capacity,
                launch_config=group.launch_config,
                max_size=group.max_size,
                min_size=group.min_size,
                name=group.name,
                placement_group=group.placement_group,
                termination_policies=', '.join(group.termination_policies),
            ))
        return dict(results=scalinggroups)

