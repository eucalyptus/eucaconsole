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

    @view_config(route_name='keypairs', renderer='../templates/keypairs/keypairs.pt', permission='view')
    def keypairs_landing(self):
        json_items_endpoint = self.request.route_url('keypairs_json')
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['name', 'fingerprint']

        return dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            json_items_endpoint=json_items_endpoint,
        )

    @view_config(route_name='keypairs_json', renderer='json', request_method='GET')
    def keypairs_json(self):
        return dict(results=self.items)


