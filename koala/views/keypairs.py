"""
Pyramid views for Eucalyptus and AWS key pairs

"""
from pyramid.view import view_config

from ..models.keypairs import KeyPair
from ..views import LandingPageView


class KeyPairsView(LandingPageView):
    def __init__(self, request):
        super(KeyPairsView, self).__init__(request)
        self.items = KeyPair.fakeall()
        self.initial_sort_key = 'name'
        self.prefix = '/keypairs'
        self.display_type = self.request.params.get('display', 'tableview')  # Set tableview as default

    @view_config(route_name='keypairs', renderer='../templates/keypairs/keypairs.pt')
    def keypairs_landing(self):
        json_items_endpoint = self.request.route_url('keypairs_json')
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['name', 'fingerprint']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name='Name'),
            dict(key='fingerprint', name='Fingerprint'),
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

    @view_config(route_name='keypairs_json', renderer='json', request_method='GET')
    def keypairs_json(self):
        return dict(results=self.items)


