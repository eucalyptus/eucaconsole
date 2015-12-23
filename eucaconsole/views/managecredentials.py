# -*- coding: utf-8 -*-
# Copyright 2013-2015 Hewlett Packard Enterprise Development LP
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
Pyramid views for Manage Credentials

"""
import logging

from urllib2 import HTTPError, URLError
from urlparse import urlparse

from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED, remember
from pyramid.view import view_config

from ..forms.login import EucaChangePasswordForm
from ..i18n import _
from ..models import Notification
from ..models.auth import User
from ..views import BaseView
from .login import PermissionCheckMixin


class ManageCredentialsView(BaseView, PermissionCheckMixin):
    template = '../templates/managecredentials.pt'

    def __init__(self, request):
        super(ManageCredentialsView, self).__init__(request)
        self.title_parts = [_(u'Manage Credentials')]
        self.changepassword_form = EucaChangePasswordForm(self.request)
        referrer = urlparse(self.request.headers['REFERER']).path
        referrer_root = referrer.split('?')[0]
        changepassword_url = self.request.route_path('changepassword')
        if referrer_root in [changepassword_url]:
            referrer = '/'  # never use the changepassword form itself as came_from
        self.came_from = self.sanitize_url(self.request.params.get('came_from', referrer))
        self.changepassword_form_errors = []
        session = self.request.session
        try:
            account = session['account']
            username = session['username']
        except KeyError:
            account = self.request.params.get('account')
            username = self.request.params.get('username')
        if account is None:  # session expired, redirect
            raise HTTPFound(location=self.request.route_path('login'))
        account_id = User.get_account_id(ec2_conn=self.get_connection(), request=self.request)
        self.render_dict = dict(
            changepassword_form=self.changepassword_form,
            changepassword_form_errors=self.changepassword_form_errors,
            password_expired=True if self.request.params.get('expired') == 'true' else False,
            came_from=self.came_from,
            account=account,
            username=username,
            account_id=account_id
        )

    @view_config(route_name='managecredentials', request_method='GET',
                 renderer=template, permission=NO_PERMISSION_REQUIRED)
    def manage_credentials(self):
        return self.render_dict

    @view_config(route_name='changepassword', request_method='POST',
                 renderer=template, permission=NO_PERMISSION_REQUIRED)
    def handle_changepassword(self):
        """Handle login form post"""
        session = self.request.session
        duration = self.request.registry.settings.get('session.cookie_expires')
        account = self.request.params.get('account')
        username = self.request.params.get('username')
        auth = self.get_euca_authenticator()
        changepassword_form = EucaChangePasswordForm(self.request, formdata=self.request.params)
        location = "{0}?{1}&{2}&{3}&{4}".format(
            self.request.route_path('managecredentials'),
            'expired=' + self.request.params.get('expired'),
            'came_from=' + self.came_from,
            'account=' + account,
            'username=' + username,
        )

        if changepassword_form.validate():
            password = self.request.params.get('current_password')
            new_password = self.request.params.get('new_password')
            new_password2 = self.request.params.get('new_password2')
            if new_password != new_password2:
                self.changepassword_form_errors.append(u'New passwords must match.')
            else:
                try:
                    creds = auth.authenticate(
                        account=account, user=username,
                        passwd=password, new_passwd=new_password, timeout=8, duration=duration)
                    # logging.debug("auth creds = "+str(creds.__dict__))
                    user_account = u'{user}@{account}'.format(user=username, account=account)
                    session['cloud_type'] = 'euca'
                    session['account'] = account
                    session['username'] = username
                    session['session_token'] = creds.session_token
                    session['access_id'] = creds.access_key
                    session['secret_key'] = creds.secret_key
                    session['account'] = account
                    session['username'] = username
                    session['region'] = 'euca'
                    session['username_label'] = user_account
                    session['dns_enabled'] = auth.dns_enabled  # this *must* be prior to line below
                    self.check_iam_perms(session, creds)
                    headers = remember(self.request, user_account)
                    msg = _(u'Successfully changed password.')
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                    return HTTPFound(location=self.came_from, headers=headers)
                except HTTPError, err:
                    # the logging here and below is really very useful when debugging login problems.
                    logging.info("http error " + str(vars(err)))
                    if err.msg == u'Unauthorized':
                        msg = _(u'Invalid user/account name and/or password.')
                        self.request.session.flash(msg, queue=Notification.ERROR)
                    return self.render_dict
                except URLError, err:
                    logging.info("url error " + str(vars(err)))
                    if str(err.reason) == 'timed out':
                        host = self._get_ufs_host_setting_()
                        msg = _(u'No response from host ') + host
                        self.request.session.flash(msg, queue=Notification.ERROR)
                    return self.render_dict
        else:
            self.request.error_messages = changepassword_form.get_errors_list()
            return self.render_dict

        return HTTPFound(location=location)
