"""
Pyramid views for Eucalyptus and AWS snapshots

"""
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..views import LandingPageView


class SnapshotsView(LandingPageView):
    def __init__(self, request):
        super(SnapshotsView, self).__init__(request)
        self.items = self.get_items()
        self.initial_sort_key = '-start_time'
        self.prefix = '/snapshots'

    def get_items(self):
        conn = self.get_connection()
        return conn.get_all_snapshots(owner='self')

    @view_config(route_name='snapshots', renderer='../templates/snapshots/snapshots.pt')
    def snapshots_landing(self):
        json_items_endpoint = self.request.route_url('snapshots_json')
        status_choices = sorted(set(item.status for item in self.items))
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        self.filter_fields = [
            LandingPageFilter(key='status', name='Status', choices=status_choices),
        ]
        more_filter_keys = [
            'id', 'name', 'owner_id', 'owner_alias', 'progress', 'size', 'start_time', 'tags', 'volume_id']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='-start_time', name='Start time'),
            dict(key='name', name='Name'),
            dict(key='owner_alias', name='Owner'),
            dict(key='progress', name='Progress'),
            dict(key='status', name='Status'),
            dict(key='volume_id', name='Volume ID'),
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
        snapshots = []
        for snapshot in self.items:
            snapshots.append(dict(
                id=snapshot.id,
                description=snapshot.description,
                name=snapshot.tags.get('Name', snapshot.id),
                owner_alias=snapshot.owner_alias,
                owner_id=snapshot.owner_id,
                progress=snapshot.progress,
                start_time=snapshot.start_time,
                status=snapshot.status,
                tags=snapshot.tags,
                volume_id=snapshot.volume_id,
                volume_size=snapshot.volume_size,
            ))
        return dict(results=snapshots)

