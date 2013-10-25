"""
Pyramid views for Eucalyptus and AWS instances

"""
from pyramid.view import view_config

from ..models.instances import Instance


class InstancesView(object):
    def __init__(self, request):
        self.request = request
        self.instances = Instance.fakeall()

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt')
    def instances_landing(self):
        return dict(instances=self.instances)

    @view_config(route_name='instances_json', renderer='json', request_method='GET')
    def instances_json(self):
        """JSON of instances"""
        return dict(results=self.instances)


