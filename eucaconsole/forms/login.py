# -*- coding: utf-8 -*-
# Copyright 2013-2014 Eucalyptus Systems, Inc.
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
Eucalyptus and AWS login forms

"""
import wtforms
from wtforms import validators, widgets

from ..i18n import _
from . import BaseSecureForm


class EucaLoginForm(BaseSecureForm):
    account = wtforms.TextField(
        _(u'Account Name'), validators=[validators.InputRequired(message=_(u'Account name is required'))])
    username = wtforms.TextField(
        _(u'Username'), validators=[validators.InputRequired(message=_(u'Username is required'))])
    password = wtforms.PasswordField(
        _(u'Password'), validators=[validators.InputRequired(message=_(u'Password is required'))])


class AWSLoginForm(BaseSecureForm):
    access_key = wtforms.TextField(_(u'Access key ID'))
    secret_key = wtforms.PasswordField(_(u'Secret key'))


class EucaChangePasswordForm(BaseSecureForm):
    current_password = wtforms.PasswordField(
        _(u'Current password'), validators=[validators.InputRequired(message=_(u'Password is required'))],
        widget=widgets.PasswordInput())
    new_password = wtforms.PasswordField(
        _(u'New password'),
        validators=[
            validators.InputRequired(message=_(u'New Password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())
    new_password2 = wtforms.PasswordField(
        _(u'Confirm new password'),
        validators=[
            validators.InputRequired(message=_(u'New Password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())


class EucaLogoutForm(BaseSecureForm):
    pass
