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
Forms for Accounts 

"""
import wtforms
from wtforms import validators

from ..i18n import _
from . import BaseSecureForm, TextEscapedField


class AccountForm(BaseSecureForm):
    """Account form
    """
    account_name_error_msg = 'Account name is required'
    account_name = TextEscapedField(
        id=u'account-name',
        label=_(u'Name'),
        validators=[validators.InputRequired(message=account_name_error_msg)],
    )

    def __init__(self, request, account=None, **kwargs):
        super(AccountForm, self).__init__(request, **kwargs)
        self.request = request
        self.account_name.error_msg = self.account_name_error_msg  # Used for Foundation Abide error message
        if account is not None:
            self.account_name.data = account.account_name


class AccountUpdateForm(BaseSecureForm):
    """Account update form
    """
    account_name_error_msg = ''
    account_name = wtforms.TextField(
        id=u'account-name',
        label=_(u'Name'),
        validators=[validators.Length(min=1, max=255)],
    )

    users_error_msg = ''
    users = wtforms.TextField(
        id=u'account-users',
        label=(u''),
        validators=[],
    )

    def __init__(self, request, account=None, **kwargs):
        super(AccountUpdateForm, self).__init__(request, **kwargs)
        self.request = request
        self.account_name.error_msg = self.account_name_error_msg  # Used for Foundation Abide error message
        if account is not None:
            self.account_name.data = account.account_name


class DeleteAccountForm(BaseSecureForm):
    """CSRF-protected form to delete a account"""
    pass

