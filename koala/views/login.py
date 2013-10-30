"""
Pyramid views for Login/Logout

"""
from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED, remember, forget
from pyramid.settings import asbool
from pyramid.view import view_config, forbidden_view_config

from ..forms.login import EucaLoginForm, AWSLoginForm


@forbidden_view_config()
def redirect_to_login_page(request):
    login_url = request.route_url('login')
    return HTTPFound(login_url)


class LoginView(object):
    template = '../templates/login.pt'

    def __init__(self, request):
        self.request = request
        self.euca_login_form = EucaLoginForm(self.request)
        self.aws_login_form = AWSLoginForm(self.request)
        self.aws_enabled = asbool(request.registry.settings.get('enable.aws'))

    @view_config(route_name='login', request_method='GET', renderer=template, permission=NO_PERMISSION_REQUIRED)
    @forbidden_view_config(request_method='GET', renderer=template)
    def login_page(self):
        return dict(
            euca_login_form=self.euca_login_form,
            aws_login_form=self.aws_login_form,
            aws_enabled=self.aws_enabled,
        )

    @view_config(route_name='login', request_method='POST', renderer=template, permission=NO_PERMISSION_REQUIRED)
    def handle_login(self):
        """Handle login form post"""

        login_type = self.request.POST.get('login_type')
        euca_login_form = self.euca_login_form
        aws_login_form = self.aws_login_form
        session = self.request.session

        if login_type == 'Eucalyptus':
            euca_login_form = EucaLoginForm(self.request, formdata=self.request.POST)
            if euca_login_form.validate():
                session['aws_login'] = False
                return dict()
        elif login_type == 'AWS':
            aws_login_form = AWSLoginForm(self.request, formdata=self.request.POST)
            if aws_login_form.validate():
                session['aws_login'] = True
                aws_access_key = self.request.POST.get('access_key')
                aws_secret_key = self.request.POST.get('secret_key')
                session['aws_access_key'] = aws_access_key
                session['aws_secret_key'] = aws_secret_key
                # TODO: Authenticate credentials with AWS
                headers = remember(self.request, aws_access_key)
                url = self.request.route_url('dashboard')
                return HTTPFound(location=url, headers=headers)
        return dict(
            euca_login_form=euca_login_form,
            aws_login_form=aws_login_form,
            aws_enabled=self.aws_enabled,
        )


class LogoutView(object):
    def __init__(self, request):
        self.request = request
        self.login_url = request.route_url('login')

    @view_config(route_name='logout')
    def logout(self):
        forget(self.request)
        self.request.session.invalidate()
        return HTTPFound(location=self.login_url)

