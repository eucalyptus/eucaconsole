"""
Pyramid views for Eucalyptus and AWS launch configurations

"""
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..models.launchconfigs import LaunchConfiguration
from ..views import LandingPageView


class LaunchConfigsView(LandingPageView):
    def __init__(self, request):
        super(LaunchConfigsView, self).__init__(request)
        self.items = LaunchConfiguration.fakeall()
        self.initial_sort_key = 'name'
        self.prefix = '/launchconfigs'

    @view_config(route_name='launchconfigs', renderer='../templates/launchconfigs/launchconfigs.pt')
    def launchconfigs_landing(self):
        json_items_endpoint = self.request.route_url('launchconfigs_json')
        key_choices = sorted(set(item.get('key') for item in self.items))
        security_group_choices = sorted(set(item.get('security_group') for item in self.items))
        image_choices = sorted(set(item.get('image') for item in self.items))
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        self.filter_fields = [
            LandingPageFilter(key='key', name='Key', choices=key_choices),
            LandingPageFilter(key='security_group', name='Security group', choices=security_group_choices),
            LandingPageFilter(key='image', name='Image', choices=image_choices),
        ]
        more_filter_keys = ['name']
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name='Name'),
            dict(key='-create_time', name='Create time (most recent first)'),
            dict(key='create_time', name='Create time (oldest first)'),
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
        return dict(results=self.items)

