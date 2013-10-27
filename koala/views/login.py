"""
Pyramid views for Login/Logout

"""
from pyramid.view import view_config


class LoginView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='login', request_method='GET', renderer='../templates/login.pt')
    def login_page(self):
        return dict()

    @view_config(route_name='login', request_method='POST')
    def handle_login(self):
        """Handle login form post"""
        pass
