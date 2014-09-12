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
Tests for change password forms

"""
import socket
from pyramid.testing import DummyRequest

from eucaconsole.forms.login import EucaChangePasswordForm
from eucaconsole.models.auth import EucaAuthenticator
from tests import BaseTestCase, BaseFormTestCase


class EucaChangePasswordFormTestCase(BaseFormTestCase):
    form_class = EucaChangePasswordForm
    request = DummyRequest()

    def test_required_fields(self):
        self.assert_required('current_password')
        self.assert_required('new_password')
        self.assert_required('new_password2')

    def test_secure_form(self):
        self.has_field('csrf_token')


class EucaChangePasswordTestCase(BaseTestCase):
    host = 'unknown_host'
    port = 8773
    auth = EucaAuthenticator(host=host, port=port)
    account = 'foo_account'
    username = 'foo'
    current_password = 'pw'
    new_password = 'newpass'
    duration = 3600


    def test_euca_authentication_failure(self):
        kwargs = dict(account=self.account, user=self.username, passwd=self.current_password,
                      new_passwd=self.new_password, duration=self.duration)
        self.assertRaises(socket.gaierror, self.auth.authenticate, **kwargs)

