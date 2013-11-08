"""
Pyramid views for Eucalyptus and AWS Elastic IP Addresses

"""
from pyramid.view import view_config

from ..models.ipaddresses import IPAddress
from ..views import LandingPageView


class IPAddressesView(LandingPageView):
    def __init__(self, request):
        super(IPAddressesView, self).__init__(request)
        self.items = IPAddress.fakeall()
        self.initial_sort_key = 'ip_address'
        self.prefix = '/ipaddresses'
        self.display_type = self.request.params.get('display', 'tableview')  # Set tableview as default

    @view_config(route_name='ipaddresses', renderer='../templates/ipaddresses/ipaddresses.pt')
    def ipaddresses_landing(self):
        json_items_endpoint = self.request.route_url('ipaddresses_json')
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['ip_address', 'instance']

        return dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
        )

    @view_config(route_name='ipaddresses_json', renderer='json', request_method='GET')
    def ipaddresses_json(self):
        return dict(results=self.items)


