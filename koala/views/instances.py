"""
Pyramid views for Eucalyptus and AWS instances

"""
from pyramid.view import view_config

from ..models.instances import Instance


@view_config(route_name='instances', renderer='../templates/instances/instances.pt')
def instances_landing(request):
    instances = Instance.fakeall()
    content = dict(
        instances=instances
    )
    return content
