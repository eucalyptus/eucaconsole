# -*- coding: utf-8 -*-
"""
Pyramid views for Change password

"""
import logging

from urllib2 import HTTPError, URLError
from urlparse import urlparse

from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED, remember
from pyramid.view import view_config

from ..forms.login import EucaChangePasswordForm
from ..views import BaseView


class ChangePasswordView(BaseView):
    template = '../templates/changepassword.pt'

    def __init__(self, request):
        super(ChangePasswordView, self).__init__(request)
        self.changepassword_form = EucaChangePasswordForm(self.request)
        referrer = urlparse(self.request.url).path
        referrer_root = referrer.split('?')[0]
        changepassword_url = self.request.route_path('changepassword')
        if referrer_root in [changepassword_url]:
            referrer = '/'  # never use the changepassword form itself as came_from
        came_from = self.request.params.get('came_from', referrer)
        if bool(urlparse(came_from).netloc):
            came_from = '/'  # Prevent arbitrary redirects
        self.came_from = came_from or '/'
        self.changepassword_form_errors = []

    @view_config(route_name='changepassword', request_method='GET', renderer=template, permission=NO_PERMISSION_REQUIRED)
    def changepassword_page(self):
        session = self.request.session
        try:
            account=session['account']
            username=session['username']
        except KeyError:
            account = self.request.params.get('account')
            username = self.request.params.get('username')
        return dict(
            changepassword_form=self.changepassword_form,
            changepassword_form_errors=self.changepassword_form_errors,
            password_expired=True if self.request.params.get('expired') == 'true' else False,
            came_from=self.came_from,
            account=account,
            username=username
        )

    @view_config(route_name='changepassword', request_method='POST', renderer=template, permission=NO_PERMISSION_REQUIRED)
    def handle_changepassword(self):
        """Handle login form post"""

        changepassword_form = self.changepassword_form
        session = self.request.session
        clchost = self.request.registry.settings.get('clchost')
        duration = self.request.registry.settings.get('session.cookie_expires')
        account="huh?"
        username="what?"

        auth = self.get_connection(conn_type='sts', cloud_type='euca')
        changepassword_form = EucaChangePasswordForm(self.request, formdata=self.request.params)
        if changepassword_form.validate():
            account = self.request.params.get('account')
            username = self.request.params.get('username')
            password = self.request.params.get('password')
            new_password = self.request.params.get('new_password')
            new_password2 = self.request.params.get('new_password2')
            if new_password != new_password2:
                self.changepassword_form_errors.append(u'New passwords must match.')
            else:
                try:
                    creds = auth.authenticate(account=account, user=username,
                                passwd=password, new_passwd=new_password, timeout=8, duration=duration)
                    #logging.debug("auth creds = "+str(creds.__dict__))
                    user_account = '{user}@{account}'.format(user=username, account=account)
                    session['cloud_type'] = 'euca'
                    session['session_token'] = creds.session_token
                    session['access_id'] = creds.access_key
                    session['secret_key'] = creds.secret_key
                    session['username_label'] = user_account
                    headers = remember(self.request, user_account)
                    return HTTPFound(location=self.came_from, headers=headers)
                except HTTPError, err:
                    logging.info("http error "+str(vars(err)))
                    if err.msg == u'Unauthorized':
                        self.changepassword_form_errors.append(u'Invalid user/account name and/or password.')
                except URLError, err:
                    logging.info("url error "+str(vars(err)))
                    if str(err.reason) == 'timed out':
                        self.changepassword_form_errors.append(u'No response from host ' + clchost)
        return dict(
            changepassword_form=changepassword_form,
            changepassword_form_errors=self.changepassword_form_errors,
            password_expired=True,
            came_from=self.came_from,
            account=account,
            username=username
        )


