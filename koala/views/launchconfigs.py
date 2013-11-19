# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS launch configurations

"""
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..views import LandingPageView


class LaunchConfigsView(LandingPageView):
    def __init__(self, request):
        super(LaunchConfigsView, self).__init__(request)
        self.items = self.get_items()
        self.initial_sort_key = 'name'
        self.prefix = '/launchconfigs'

    def get_items(self):
        conn = self.get_connection(conn_type='autoscale')
        return conn.get_all_launch_configurations() if conn else []

    @view_config(route_name='launchconfigs', renderer='../templates/launchconfigs/launchconfigs.pt')
    def launchconfigs_landing(self):
        json_items_endpoint = self.request.route_url('launchconfigs_json')
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        image_id_choices = sorted(set(item.image_id for item in self.items))
        self.filter_fields = [
            LandingPageFilter(key='launch_config', name='Image', choices=image_id_choices),
        ]
        more_filter_keys = ['image_id', 'name', 'security_groups']
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name='Name'),
            dict(key='-created_time', name='Created time (recent first)'),
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

    @view_config(route_name='launchconfigs_json', renderer='json', request_method='GET')
    def launchconfigs_json(self):
        launchconfigs = []
        for launchconfig in self.items:
            security_groups = ', '.join(launchconfig.security_groups)
            launchconfigs.append(dict(
                created_time=launchconfig.created_time.isoformat(),
                image_id=launchconfig.image_id,
                instance_monitoring=bool(launchconfig.instance_monitoring),
                kernel_id=launchconfig.kernel_id,
                key_name=launchconfig.key_name,
                name=launchconfig.name,
                ramdisk_id=launchconfig.ramdisk_id,
                security_groups=security_groups,
                user_data=launchconfig.user_data,
            ))
        return dict(results=launchconfigs)

