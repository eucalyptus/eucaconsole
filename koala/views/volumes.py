"""
Pyramid views for Eucalyptus and AWS volumes

"""
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..views import LandingPageView


class VolumesView(LandingPageView):
    def __init__(self, request):
        super(VolumesView, self).__init__(request)
        self.items = self.get_items()
        self.initial_sort_key = '-create_time'
        self.prefix = '/volumes'

    def get_items(self):
        conn = self.get_connection()
        return conn.get_all_volumes()

    @view_config(route_name='volumes', renderer='../templates/volumes/volumes.pt')
    def volumes_landing(self):
        json_items_endpoint = self.request.route_url('volumes_json')
        status_choices = sorted(set(item.status for item in self.items))
        zone_choices = sorted(set(item.zone for item in self.items))
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        self.filter_fields = [
            LandingPageFilter(key='status', name='Status', choices=status_choices),
            LandingPageFilter(key='zone', name='Availability zone', choices=zone_choices),
            # LandingPageFilter(key='tags', name='Tags'),
        ]
        more_filter_keys = ['id', 'instance', 'name', 'size', 'snapshot_id', 'create_time', 'tags']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='-create_time', name='Create time'),
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

    @view_config(route_name='volumes_json', renderer='json', request_method='GET')
    def volumes_json(self):
        volumes = []
        for volume in self.items:
            volumes.append(dict(
                create_time=volume.create_time,
                id=volume.id,
                instance=volume.attach_data.instance_id,
                name=volume.tags.get('Name', volume.id),
                snapshot_id=volume.snapshot_id,
                size=volume.size,
                status=volume.status,
                zone=volume.zone,
                tags=volume.tags,
            ))
        return dict(results=volumes)

