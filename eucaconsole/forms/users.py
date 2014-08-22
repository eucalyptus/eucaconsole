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
Forms for Users 

"""
import simplejson as json

from boto.exception import BotoServerError

import wtforms
from wtforms import validators
from wtforms import widgets

from ..i18n import _
from . import BaseSecureForm, TextEscapedField


class UserForm(BaseSecureForm):
    """User form
       Note: no need to add a 'users' field.  Use the user_editor panel (in a template) instead
       Only need to initialize as a secure form to generate CSRF token
    """
    # these fields used for new user form
    random_password = wtforms.BooleanField(label=_(u"Create and download random password"))
    access_keys = wtforms.BooleanField(label=_(u"Create and download access keys"))
    allow_all = wtforms.BooleanField(label=_(u"Allow read/write access to all resource except users and groups"))

    path = TextEscapedField(label=_(u"Path"), default="/")

    # additional items used for update user form
    user_name = wtforms.TextField(label=_(u"Name"))
    email = wtforms.TextField(label=_(u"E-mail address"))
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

    download_keys = wtforms.BooleanField(label=_(u"Download keys after generation"))

    def __init__(self, request, user=None, **kwargs):
        super(UserForm, self).__init__(request, **kwargs)
        self.user = user
        if user is not None:
            self.user_name.data = user.user_name
            self.path.data = user.path

    def setLowest(self, item, val):
        """ This function sets the field data value if the new value is lower than the current one """
        if item.data is None or item.data > val:
            item.data = val

class DisableUserForm(BaseSecureForm):
    """CSRF-protected form to disable a user"""
    pass

class EnableUserForm(BaseSecureForm):
    """CSRF-protected form to enable a user"""
    random_password = wtforms.BooleanField(label=_(u"Create and download random password"))

class ChangePasswordForm(BaseSecureForm):
    """CSRF-protected form to change a password """
    password = wtforms.PasswordField(
        _(u'Your password'),
        validators=[
            validators.InputRequired(message=_(u'A password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())

class GeneratePasswordForm(BaseSecureForm):
    """CSRF-protected form to generate a random password"""
    password = wtforms.PasswordField(
        _(u'Your password'),
        validators=[
            validators.InputRequired(message=_(u'A password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())

class DeleteUserForm(BaseSecureForm):
    """CSRF-protected form to delete a user"""
    pass

class AddToGroupForm(BaseSecureForm):
    group_error_msg = _(u'Group is required')
    group_name = wtforms.SelectField(
        validators=[validators.InputRequired(message=group_error_msg)],
    )
    def __init__(self, request, groups=None, **kwargs):
        super(AddToGroupForm, self).__init__(request, **kwargs)
        if groups is not None:
            choices = [(group, group) for group in groups]
            self.group_name.choices = choices
        else:
            self.group_name.choices = [('', '')]

