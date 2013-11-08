"""
Pyramid views for Eucalyptus and AWS snapshots

"""
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..models.snapshots import Snapshot
from ..views import LandingPageView


class SnapshotsView(LandingPageView):
    def __init__(self, request):
        super(SnapshotsView, self).__init__(request)
        self.items = Snapshot.fakeall()
        self.initial_sort_key = '-start_time'
        self.prefix = '/snapshots'

    @view_config(route_name='snapshots', renderer='../templates/snapshots/snapshots.pt')
    def snapshots_landing(self):
        json_items_endpoint = self.request.route_url('snapshots_json')
        status_choices = sorted(set(item.get('status') for item in self.items))
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        self.filter_fields = [
            LandingPageFilter(key='status', name='Status', choices=status_choices),
            # LandingPageFilter(key='tags', name='Tags'),
        ]
        more_filter_keys = ['id', 'name', 'size', 'volume', 'start_time', 'tags']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='-start_time', name='Start time'),
            dict(key='name', name='Name'),
            dict(key='status', name='Status'),
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

    @view_config(route_name='snapshots_json', renderer='json', request_method='GET')
    def snapshots_json(self):
        return dict(results=self.items)

