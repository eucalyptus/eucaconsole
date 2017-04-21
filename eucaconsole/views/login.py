# -*- coding: utf-8 -*-
# Copyright 2013-2017 Ent. Services Development Corporation LP
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Pyramid views for Login/Logout

"""
import base64
import collections
import ConfigParser
import httplib
import os
import urllib
import logging
import simplejson as json
from urllib2 import HTTPError, URLError
from urlparse import urlparse
from boto.connection import AWSAuthConnection
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED, remember, forget
from pyramid.settings import asbool
from pyramid.view import view_config, forbidden_view_config

from ..forms.login import EucaLoginForm, EucaLogoutForm, AWSLoginForm
from ..i18n import _
from ..models import Notification
from ..models.auth import AWSAuthenticator, ConnectionManager
from ..views import BaseView
from ..views import JSONResponse
from ..constants import AWS_REGIONS


INVALID_SSL_CERT_MSG = _(u"This cloud's SSL server certificate isn't valid. Please contact your cloud administrator.")


@forbidden_view_config()
def redirect_to_login_page(request):
    login_url = request.route_path('login')
    return HTTPFound(login_url)


class PermissionCheckMixin(object):
    def check_iam_perms(self, session, creds):
        region = session.get('region')
        iam_conn = self.get_connection(
            conn_type='iam', cloud_type='euca', region=region,
            access_key=creds.access_key, secret_key=creds.secret_key, security_token=creds.session_token)
        account = session['account']
        session['account_access'] = True if account == 'eucalyptus' else False
        session['user_access'] = False
        try:
            iam_conn.get_all_users(path_prefix="/notlikely")
            session['user_access'] = True
        except BotoServerError:
            pass
        session['group_access'] = False
        try:
            iam_conn.get_all_groups(path_prefix="/notlikely")
            session['group_access'] = True
        except BotoServerError:
            pass
        session['role_access'] = False
        try:
            iam_conn.list_roles(path_prefix="/notlikely")
            session['role_access'] = True
        except BotoServerError:
            pass


class LoginView(BaseView, PermissionCheckMixin):
    TEMPLATE = '../templates/login.pt'

    def __init__(self, request):
        super(LoginView, self).__init__(request)
        self.title_parts = [_(u'Login')]
        self.euca_login_form = EucaLoginForm(self.request, formdata=self.request.params or None)
        self.aws_login_form = AWSLoginForm(self.request, formdata=self.request.params or None)
        self.aws_enabled = asbool(request.registry.settings.get('enable.aws'))
        referrer = urlparse(self.request.url).path
        login_url = self.request.route_path('login')
        logout_url = self.request.route_path('logout')
        if referrer in [login_url, logout_url]:
            referrer = '/'  # never use the login form (or logout view) itself as came_from
        self.came_from = self.sanitize_url(self.request.params.get('came_from', referrer))
        self.login_form_errors = []
        self.duration = str(int(self.request.registry.settings.get('session.cookie_expires')) + 60)
        self.admin_duration = str(int(self.request.registry.settings.get('session.max_admin_expires', 3600)) + 60)
        self.login_refresh = str(int(self.request.registry.settings.get('session.timeout')) - 60)
        self.secure_session = asbool(self.request.registry.settings.get('session.secure', False))
        self.https_proxy = self.request.environ.get('HTTP_X_FORWARDED_PROTO') == 'https'
        self.https_scheme = self.request.scheme == 'https'

        self.oidc_host = self.request.registry.settings.get('oidc.hostname', None)
        oidc_enabled = self.oidc_host is not None
        login_link = ''
        if oidc_enabled:
            oidc_scope = self.request.registry.settings.get('oidc.scope', None)
            creds = self.load_oidc_credentials(self.request.registry.settings)
            if creds:
                self.oidc_client_id = creds.client_id
                self.oidc_client_secret = creds.client_secret
                self.oidc_console_host = self.request.registry.settings.get('oidc.console.hostname', None)
                login_params = dict(
                    scope=oidc_scope,
                    redirect_uri='https://{0}/login'.format(self.oidc_console_host),
                    access_type='online',
                    response_type='code',
                    client_id=self.oidc_client_id
                )
                login_link = 'https://{0}/v2/oauth2/authorize?'.format(self.oidc_host) + urllib.urlencode(login_params)
            else:
                oidc_enabled = False
        options_json = BaseView.escape_json(json.dumps(dict(
            account=request.params.get('account', default=''),
            username=request.params.get('username', default=''),
            oidcLoginLink=login_link
        )))
        self.render_dict = dict(
            https_required=self.show_https_warning(),
            euca_login_form=self.euca_login_form,
            aws_login_form=self.aws_login_form,
            login_form_errors=self.login_form_errors,
            aws_enabled=self.aws_enabled,
            duration=self.duration,
            login_refresh=self.login_refresh,
            came_from=self.came_from,
            controller_options_json=options_json,
            oidc_enabled=oidc_enabled,
            oidc_link_text=self.request.registry.settings.get('oidc.login.button.label', 'oidc login')
        )

    def show_https_warning(self):
        if self.secure_session and not (any([self.https_proxy, self.https_scheme])):
            return True
        return False

    @view_config(route_name='login', request_method='GET', renderer=TEMPLATE, permission=NO_PERMISSION_REQUIRED)
    @forbidden_view_config(request_method='GET', renderer=TEMPLATE)
    def login_page(self):
        if self.request.is_xhr:
            message = getattr(self.request.exception, 'message', _(u"Session Timed Out"))
            status = getattr(self.request.exception, 'status', "403 Forbidden")
            status = int(status[:status.index(' ')]) or 403
            return JSONResponse(status=status, message=message)
        state = self.request.params.get('state')
        if state and state.find('oidc-') == 0:
            try:
                # ok, it's oidc, validate and get token
                auth_code = self.request.params.get('code')
                # post to token service
                data = {
                    'grant_type': 'authorization_code',
                    'code': auth_code,
                    'redirect_uri': 'https://%s/login' % self.oidc_console_host
                }
                conn = httplib.HTTPSConnection(self.oidc_host, 443, timeout=300)
                auth_string = base64.b64encode(
                    ('%s:%s' % (self.oidc_client_id, self.oidc_client_secret)).encode('latin1')
                ).strip()
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/vnd.api+json',
                    'Authorization': 'Basic ' + auth_string
                }
                # Is it worth looking this url up via .well-known/openid-configuration?
                # It's part of the API standard, so not likely to change
                conn.request('POST', '/v2/oauth2/token', urllib.urlencode(data), headers)
                response = conn.getresponse()
                if response.status == 401:
                    self.login_form_errors.append("OAuth authentication failed")
                body = response.read()
                token = json.loads(body)
                return self.handle_web_identity_login(token)
            except BotoServerError as err:
                if err.message.find('Invalid role ARN') > -1:
                    msg = _(u'Unable to login, check that you have the correct account name')
                else:
                    msg = _(u'Unable to login, ') + err.message
                self.request.session.flash(msg, queue=Notification.ERROR)
                
        return self.render_dict

    @view_config(route_name='login', request_method='POST', renderer=TEMPLATE, permission=NO_PERMISSION_REQUIRED)
    def handle_login(self):
        """Handle login form post"""

        login_type = self.request.params.get('login_type')

        if login_type == 'Eucalyptus':
            return self.handle_euca_login()
        elif login_type == 'AWS':
            return self.handle_aws_login()

        return self.render_dict

    def handle_web_identity_login(self, token):
        auth = self.get_oidc_authenticator()
        session = self.request.session

        try:
            state = token['state']
            # try authentication with default of dns_enabled = True. Set to False if we fail
            (oidc, euca_region, account_name) = state.split('-', 2)
            euca_region = base64.urlsafe_b64decode(euca_region)
            # and if that also fails, let that error raise up
            creds = auth.authenticate(token=token, account_name=account_name, timeout=8, duration=self.duration)
            # now that we authenticated, extract info from token
            jwt_body = token['id_token'].split('.')[1]
            jwt_info = json.loads(base64.urlsafe_b64decode(jwt_body + '=='))
            account = account_name
            username = jwt_info['preferred_username']
            logging.info(u"Authenticated OIDC user: {user} from {ip}".format(
                user=username, ip=BaseView.get_remote_addr(self.request)
            ))
            default_region = self.request.registry.settings.get('default.region', 'euca')
            user_account = u'{user} : {account}'.format(user=username, account=account)
            session.invalidate()  # Refresh session
            session['cloud_type'] = 'euca'
            session['auth_type'] = 'oidc'
            session['account'] = account
            session['username'] = username
            self._assign_session_creds(session, creds)
            session['region'] = euca_region if euca_region != '' else default_region
            session['username_label'] = user_account
            session['dns_enabled'] = auth.dns_enabled  # this *must* be prior to line below
            session['supported_platforms'] = self.get_account_attributes(['supported-platforms'])
            session['default_vpc'] = self.get_account_attributes(['default-vpc'])

            # handle checks for IAM perms
            self.check_iam_perms(session, creds)
            headers = remember(self.request, user_account)
            return HTTPFound(location=self.came_from, headers=headers)
        except HTTPError as err:
            logging.info("http error " + str(vars(err)))
            if err.code == 403:  # password expired
                changepwd_url = self.request.route_path('managecredentials')
                return HTTPFound(
                    changepwd_url + ("?came_from=&expired=true&account=%s&username=%s" % (account, username))
                )
            elif err.msg == u'Unauthorized':
                msg = _(u'Invalid user/account name and/or password.')
                self.login_form_errors.append(msg)
        except URLError as err:
            logging.info("url error " + str(vars(err)))
            # if str(err.reason) == 'timed out':
            # opened this up since some other errors should be reported as well.
            if err.reason.find('ssl') > -1:
                msg = INVALID_SSL_CERT_MSG
            else:
                msg = _(u'No response from host')
            self.login_form_errors.append(msg)
        return self.render_dict

    def handle_euca_login(self):
        new_passwd = None
        auth = self.get_euca_authenticator()
        session = self.request.session

        if self.euca_login_form.validate():
            account = self.request.params.get('account')
            username = self.request.params.get('username')
            password = self.request.params.get('password')
            euca_region = self.request.params.get('euca-region')
            try:
                if username == 'admin':
                    self.duration = min(self.duration, self.admin_duration)
                # TODO: also return dns enablement
                creds = auth.authenticate(
                    account=account, user=username, passwd=password,
                    new_passwd=new_passwd, timeout=8, duration=self.duration)
                logging.info(u"Authenticated Eucalyptus user: {acct}/{user} from {ip}".format(
                    acct=account, user=username, ip=BaseView.get_remote_addr(self.request)))
                default_region = self.request.registry.settings.get('default.region', 'euca')
                user_account = u'{user}@{account}'.format(user=username, account=account)
                session.invalidate()  # Refresh session
                session['cloud_type'] = 'euca'
                session['auth_type'] = 'password'
                session['account'] = account
                session['username'] = username
                self._assign_session_creds(session, creds)
                session['region'] = euca_region if euca_region != '' else default_region
                session['username_label'] = user_account
                session['dns_enabled'] = auth.dns_enabled  # this *must* be prior to line below
                session['supported_platforms'] = self.get_account_attributes(['supported-platforms'])
                session['default_vpc'] = self.get_account_attributes(['default-vpc'])

                # handle checks for IAM perms
                self.check_iam_perms(session, creds)
                headers = remember(self.request, user_account)
                return HTTPFound(location=self.came_from, headers=headers)
            except HTTPError as err:
                logging.info("http error " + str(vars(err)))
                if err.code == 403:  # password expired
                    changepwd_url = self.request.route_path('managecredentials')
                    return HTTPFound(
                        changepwd_url + ("?came_from=&expired=true&account=%s&username=%s" % (account, username))
                    )
                elif err.msg == u'Unauthorized':
                    msg = _(u'Invalid user/account name and/or password.')
                    self.login_form_errors.append(msg)
            except URLError as err:
                logging.info("url error " + str(vars(err)))
                # if str(err.reason) == 'timed out':
                # opened this up since some other errors should be reported as well.
                if err.reason.find('ssl') > -1:
                    msg = INVALID_SSL_CERT_MSG
                else:
                    msg = _(u'No response from host')
                self.login_form_errors.append(msg)
        return self.render_dict

    def handle_aws_login(self):
        session = self.request.session
        if self.aws_login_form.validate():
            package = self.request.params.get('package')
            package = base64.decodestring(package)
            aws_region = self.request.params.get('aws-region')
            validate_certs = asbool(self.request.registry.settings.get('connection.ssl.validation', False))
            conn = AWSAuthConnection(None, aws_access_key_id='', aws_secret_access_key='')
            ca_certs_file = conn.ca_certificates_file
            conn = None
            ca_certs_file = self.request.registry.settings.get('connection.ssl.certfile', ca_certs_file)
            auth = AWSAuthenticator(package=package, validate_certs=validate_certs, ca_certs=ca_certs_file)
            try:
                creds = auth.authenticate(timeout=10)
                logging.info(u"Authenticated AWS user from {ip}".format(ip=BaseView.get_remote_addr(self.request)))
                default_region = self.request.registry.settings.get('aws.default.region', 'us-east-1')
                session.invalidate()  # Refresh session
                session['cloud_type'] = 'aws'
                session['auth_type'] = 'keys'
                self._assign_session_creds(session, creds)
                last_visited_aws_region = [reg for reg in AWS_REGIONS if reg.get('name') == aws_region]
                session['region'] = aws_region if last_visited_aws_region else default_region
                session['username_label'] = u'{user}...@AWS'.format(user=creds.access_key[:8])
                session['supported_platforms'] = self.get_account_attributes(['supported-platforms'])
                session['default_vpc'] = self.get_account_attributes(['default-vpc'])
                conn = ConnectionManager.aws_connection(
                    session['region'], creds.access_key, creds.secret_key, creds.session_token, 'vpc')
                vpcs = conn.get_all_vpcs()
                if not vpcs or len(vpcs) == 0:
                    # remove vpc from supported-platforms
                    if 'VPC' in session.get('supported_platforms', []):
                        session.get('supported_platforms').remove('VPC')
                headers = remember(self.request, creds.access_key[:8])
                return HTTPFound(location=self.came_from, headers=headers)
            except HTTPError as err:
                if err.msg == 'Forbidden':
                    msg = _(u'Invalid access key and/or secret key.')
                    self.login_form_errors.append(msg)
            except URLError as err:
                if err.reason.find('ssl') > -1:
                    msg = INVALID_SSL_CERT_MSG
                else:
                    msg = _(u'No response from host')
                self.login_form_errors.append(msg)
        return self.render_dict

    @staticmethod
    def _assign_session_creds(session, creds):
        session['session_token'] = creds.session_token
        session['access_id'] = creds.access_key
        session['secret_key'] = creds.secret_key

    @staticmethod
    def load_oidc_credentials(settings):
        source = settings.get('oidc.client.ini', 'oidc-credentials.ini')
        if not os.path.exists(source):
            logging.error("missing the oidc.client.ini file, refer to this setting in the console.ini")
            return None
        else:
            try:
                ini = ConfigParser.ConfigParser()
                with open(source) as f:
                    ini.readfp(f)
            except ConfigParser.Error as err:
                logging.error("Error parsing the oidc.client.ini file: " + err.message)
                return None

        try:
            Creds = collections.namedtuple('oidc_creds', 'client_id client_secret')
            return Creds(
                client_id=ini.get('general', 'oidc.client.id'),
                client_secret=ini.get('general', 'oidc.client.secret')
            )
        except ConfigParser.Error as err:
            logging.error("Error reading the oidc.client.ini file: " + err.message)
            return None


class LogoutView(BaseView):
    def __init__(self, request):
        super(LogoutView, self).__init__(request)
        self.request = request
        self.login_url = request.route_path('login')
        self.euca_logout_form = EucaLogoutForm(self.request, formdata=self.request.params or None)

    @view_config(route_name='logout', request_method='POST')
    def logout(self):
        if self.euca_logout_form.validate():
            forget(self.request)
            self.request.session.invalidate()
        return HTTPFound(location=self.login_url)
