# -*- coding: utf-8 -*-
"""
Pyramid views for Login/Logout

"""
from urllib2 import HTTPError, URLError

from beaker.cache import cache_managers
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.security import NO_PERMISSION_REQUIRED, remember, forget
from pyramid.settings import asbool
from pyramid.view import view_config, forbidden_view_config

from ..forms.login import EucaLoginForm, AWSLoginForm
from ..models.auth import AWSAuthenticator, EucaAuthenticator, ConnectionManager


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
        referrer = self.request.url
        login_url = self.request.route_url('login')
        logout_url = self.request.route_url('logout')
        if referrer in [login_url, logout_url]:
            referrer = '/'  # never use the login form (or logout view) itself as came_from
        self.came_from = self.request.params.get('came_from', referrer)
        self.login_form_errors = []

    @view_config(route_name='login', request_method='GET', renderer=template, permission=NO_PERMISSION_REQUIRED)
    @forbidden_view_config(request_method='GET', renderer=template)
    def login_page(self):
        return dict(
            euca_login_form=self.euca_login_form,
            aws_login_form=self.aws_login_form,
            login_form_errors=self.login_form_errors,
            aws_enabled=self.aws_enabled,
            came_from=self.came_from,
        )

    @view_config(route_name='login', request_method='POST', renderer=template, permission=NO_PERMISSION_REQUIRED)
    def handle_login(self):
        """Handle login form post"""

        login_type = self.request.params.get('login_type')
        euca_login_form = self.euca_login_form
        aws_login_form = self.aws_login_form
        session = self.request.session
        clchost = self.request.registry.settings.get('clchost')
        duration = self.request.registry.settings.get('session.cookie_expires')
        new_passwd = None

        if login_type == 'Eucalyptus':
            auth = EucaAuthenticator(host=clchost, duration=duration)
            euca_login_form = EucaLoginForm(self.request, formdata=self.request.params)
            if euca_login_form.validate():
                account = self.request.params.get('account')
                username = self.request.params.get('username')
                password = self.request.params.get('password')
                try:
                    creds = auth.authenticate(
                        account=account, user=username, passwd=password, new_passwd=new_passwd, timeout=8)
                    user_account = '{user}@{account}'.format(user=username, account=account)
                    session['cloud_type'] = 'euca'
                    session['session_token'] = creds.session_token
                    session['access_id'] = creds.access_key
                    session['secret_key'] = creds.secret_key
                    session['username_label'] = '{user}@{account}'.format(user=username, account=account)
                    headers = remember(self.request, user_account)
                    return HTTPFound(location=self.came_from, headers=headers)
                except HTTPError, err:
                    if err.msg == u'Unauthorized':
                        msg = _(u'Invalid user/account name and/or password.')
                        self.login_form_errors.append(msg)
                except URLError, err:
                    if str(err.reason) == 'timed out':
                        msg = _(u'No response from host ')
                        self.login_form_errors.append(msg + clchost)
        elif login_type == 'AWS':
            aws_login_form = AWSLoginForm(self.request, formdata=self.request.params)
            if aws_login_form.validate():
                aws_access_key = self.request.params.get('access_key')
                aws_secret_key = self.request.params.get('secret_key')
                try:
                    auth = AWSAuthenticator(key_id=aws_access_key, secret_key=aws_secret_key, duration=duration)
                    creds = auth.authenticate(timeout=10)
                    default_region = self.request.registry.settings.get('aws.default.region', 'us-east-1')
                    session['cloud_type'] = 'aws'
                    session['session_token'] = creds.session_token
                    session['access_id'] = creds.access_key
                    session['secret_key'] = creds.secret_key
                    session['region'] = default_region
                    session['username_label'] = '{user}...@AWS'.format(user=aws_access_key[:8])
                    # Save EC2 Connection object in cache
                    ConnectionManager.aws_connection(
                        default_region, creds.access_key, creds.secret_key, creds.session_token, 'ec2')
                    headers = remember(self.request, aws_access_key)
                    return HTTPFound(location=self.came_from, headers=headers)
                except HTTPError, err:
                    if err.msg == 'Forbidden':
                        msg = _(u'Invalid access key and/or secret key.')
                        self.login_form_errors.append(msg)
                except URLError, err:
                    if str(err.reason) == 'timed out':
                        msg = _(u'No response from host ')
                        self.login_form_errors.append(msg + clchost)
        return dict(
            euca_login_form=euca_login_form,
            aws_login_form=aws_login_form,
            login_form_errors=self.login_form_errors,
            aws_enabled=self.aws_enabled,
            came_from=self.came_from,
        )


class LogoutView(object):
    def __init__(self, request):
        self.request = request
        self.login_url = request.route_url('login')

    @view_config(route_name='logout')
    def logout(self):
        forget(self.request)
        # Clear session
        self.request.session.invalidate()
        # Empty Beaker cache to clear connection objects
        for _cache in cache_managers.values():
            _cache.clear()
        return HTTPFound(location=self.login_url)

