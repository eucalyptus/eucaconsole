"""
Pyramid views for Eucalyptus and AWS instances

"""
from pyramid.view import view_config

from ..models import LandingPageFilter
from ..models.instances import Instance
from ..views import LandingPageView


class InstancesView(LandingPageView):
    def __init__(self, request):
        super(InstancesView, self).__init__(request)
        self.instances = Instance.fakeall()

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt', permission='view')
    def instances_landing(self):
        json_items_endpoint = self.request.route_url('instances_json')
        status_choices = sorted(set(instance.get('status') for instance in self.instances))
        root_device_choices = sorted(set(instance.get('root_device') for instance in self.instances))
        instance_type_choices = sorted(set(instance.get('instance_type') for instance in self.instances))
        security_group_choices = sorted(set(instance.get('security_group') for instance in self.instances))
        avail_zone_choices = sorted(set(instance.get('availability_zone') for instance in self.instances))
        self.filter_fields = [
            LandingPageFilter(key='status', name='Status', choices=status_choices),
            LandingPageFilter(key='root_device', name='Root device', choices=root_device_choices),
            LandingPageFilter(key='instance_type', name='Instance type', choices=instance_type_choices),
            LandingPageFilter(key='security_group', name='Security group', choices=security_group_choices),
            LandingPageFilter(key='availability_zone', name='Availability zone', choices=avail_zone_choices),
            LandingPageFilter(key='tags', name='Tags'),
        ]
        more_filter_keys = ['instance_id']
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys

        return dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            json_items_endpoint=json_items_endpoint,
        )

    @view_config(route_name='instances_json', renderer='json', request_method='GET')
    def instances_json(self):
        """JSON of instances"""
        return dict(results=self.instances)


