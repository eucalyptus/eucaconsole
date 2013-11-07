"""
Pyramid views for Dashboard

"""
from pyramid.view import view_config
from ..models.instances import Instance


class DashboardView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='dashboard', request_method='GET', renderer='../templates/dashboard.pt')
    def dashboard_home(self):
        instances = Instance.fakeall()
        instances_running_count = Instance.get_count_by_state(items=instances, state='Running')
        instances_stopped_count = Instance.get_count_by_state(items=instances, state='Stopped')
        return dict(
            instances_running_count=instances_running_count,
            instances_stopped_count=instances_stopped_count,
        )
