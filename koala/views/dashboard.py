"""
Pyramid views for Dashboard

"""
from pyramid.view import view_config


class DashboardView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='dashboard', request_method='GET', renderer='../templates/dashboard.pt')
    def dashboard_home(self):
        return dict()
