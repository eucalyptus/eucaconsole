"""
Pyramid views for Login/Logout

"""
from pyramid.httpexceptions import HTTPFound
from pyramid.settings import asbool
from pyramid.view import view_config

from ..forms.login import EucaLoginForm, AWSLoginForm


class LoginView(object):
    template = '../templates/login.pt'

    def __init__(self, request):
        self.request = request
        self.euca_login_form = EucaLoginForm(self.request)
        self.aws_login_form = AWSLoginForm(self.request)
        self.aws_enabled = asbool(request.registry.settings.get('enable.aws'))

    @view_config(route_name='login', request_method='GET', renderer=template)
    def login_page(self):
        return dict(
            euca_login_form=self.euca_login_form,
            aws_login_form=self.aws_login_form,
            aws_enabled=self.aws_enabled,
        )

    @view_config(route_name='login', request_method='POST', renderer=template)
    def handle_login(self):
        """Handle login form post"""

        login_type = self.request.POST.get('login_type')
        euca_login_form = self.euca_login_form
        aws_login_form = self.aws_login_form
        session = self.request.session

        if login_type == 'Eucalyptus':
            euca_login_form = EucaLoginForm(self.request, formdata=self.request.POST)
            if euca_login_form.validate():
                return dict()
        elif login_type == 'AWS':
            aws_login_form = AWSLoginForm(self.request, formdata=self.request.POST)
            if aws_login_form.validate():
                # TODO: Authenticate credentials with AWS
                session['aws_login'] = True
                session['aws_access_key'] = self.request.POST.get('access_key')
                session['aws_secret_key'] = self.request.POST.get('secret_key')
                url = self.request.route_url('dashboard')
                return HTTPFound(url)
        return dict(
            euca_login_form=euca_login_form,
            aws_login_form=aws_login_form,
        )
