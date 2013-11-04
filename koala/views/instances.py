"""
Pyramid views for Eucalyptus and AWS instances

"""
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..models.instances import Instance


class InstancesView(object):
    def __init__(self, request):
        self.request = request
        self.instances = Instance.fakeall()

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt', permission='view')
    def instances_landing(self):
        # We could build the status choices list from Invoice.STATUS_CHOICES, but let's restrict based on the instances
        json_items_endpoint = self.request.route_url('instances_json')
        status_choices = set(instance.get('status') for instance in self.instances)
        filter_fields = [
            LandingPageFilter(key='status', name='status', choices=status_choices),
            LandingPageFilter(key='root_device', name='Root device'),
            LandingPageFilter(key='instance_type', name='Instance type'),
            LandingPageFilter(key='security_group', name='Security group'),
            LandingPageFilter(key='availability_zone', name='Availability zone'),
            LandingPageFilter(key='tags', name='Tags'),
        ]
        filter_keys = [field.key for field in filter_fields]

        return dict(
            instances=self.instances,
            filter_fields=filter_fields,
            filter_keys=filter_keys,
            json_items_endpoint=json_items_endpoint,
        )

    @view_config(route_name='instances_json', renderer='json', request_method='GET')
    def instances_json(self):
        """JSON of instances"""
        return dict(results=self.instances)


