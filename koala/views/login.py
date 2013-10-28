"""
Pyramid views for Login/Logout

"""
from pyramid.view import view_config

from ..forms.login import EucaLoginForm


class LoginView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='login', request_method='GET', renderer='../templates/login.pt')
    def login_page(self):
        form = EucaLoginForm(self.request)
        return dict(form=form)

    @view_config(route_name='login', request_method='POST', renderer='../templates/login.pt')
    def handle_login(self):
        """Handle login form post"""
        form = EucaLoginForm(self.request, formdata=self.request.POST)
        if form.validate():
            return dict()
        return dict(form=form)
