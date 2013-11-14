# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS scaling groups

"""
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..models.scalinggroups import AutoScalingGroup
from ..views import LandingPageView


class ScalingGroupsView(LandingPageView):
    def __init__(self, request):
        super(ScalingGroupsView, self).__init__(request)
        self.items = AutoScalingGroup.fakeall()
        self.initial_sort_key = 'name'
        self.prefix = '/scalinggroups'

    @view_config(route_name='scalinggroups', renderer='../templates/scalinggroups/scalinggroups.pt')
    def scalinggroups_landing(self):
        json_items_endpoint = self.request.route_url('scalinggroups_json')
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        instance_health_choices = ['All healthy', 'Unhealthy']
        self.filter_fields = [
            LandingPageFilter(key='instance_health', name='Instance Health', choices=instance_health_choices),
        ]
        more_filter_keys = ['name', 'launch_config']
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name='Name'),
            dict(key='instance_health', name='Instance Health'),
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
        return dict(results=self.items)

