"""
Pyramid views for Eucalyptus and AWS security groups

"""
from pyramid.view import view_config

from ..models.securitygroups import SecurityGroup
from ..views import LandingPageView


class SecurityGroupsView(LandingPageView):
    def __init__(self, request):
        super(SecurityGroupsView, self).__init__(request)
        self.items = SecurityGroup.fakeall()
        self.initial_sort_key = 'name'
        self.prefix = '/securitygroups'
        self.display_type = self.request.params.get('display', 'tableview')  # Set tableview as default

    @view_config(route_name='securitygroups', renderer='../templates/securitygroups/securitygroups.pt')
    def securitygroups_landing(self):
        json_items_endpoint = self.request.route_url('securitygroups_json')
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['name', 'description', 'tags']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name='Name'),
            dict(key='description', name='Description'),
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

    @view_config(route_name='securitygroups_json', renderer='json', request_method='GET')
    def securitygroups_json(self):
        return dict(results=self.items)


