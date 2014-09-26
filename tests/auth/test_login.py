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
Tests for login forms

"""
from urllib2 import HTTPError, URLError

import boto
from pyramid.security import Authenticated
from pyramid.testing import DummyRequest

from eucaconsole.forms.login import AWSLoginForm, EucaLoginForm
from eucaconsole.models.auth import AWSAuthenticator, EucaAuthenticator, User, groupfinder
from eucaconsole.views import BaseView
from tests import BaseTestCase, BaseFormTestCase


class EucaLoginFormTestCase(BaseFormTestCase):
    form_class = EucaLoginForm
    request = DummyRequest()

    def test_required_fields(self):
        self.assert_required('account')
        self.assert_required('username')
        self.assert_required('password')

    def test_secure_form(self):
        self.has_field('csrf_token')


class AWSLoginFormTestCase(BaseFormTestCase):
    form_class = AWSLoginForm
    request = DummyRequest()

    def test_required_fields(self):
        self.has_field('access_key')
        self.has_field('secret_key')

    def test_secure_form(self):
        self.has_field('csrf_token')


class EucaAuthTestCase(BaseTestCase):
    host = 'unknown_host'
    port = 8773
    auth = EucaAuthenticator(host=host, port=port)
    account = 'foo_account'
    username = 'foo'
    password = 'pw'
    duration = 3600

    def test_euca_authentication_failure(self):
        kwargs = dict(account=self.account, user=self.username, passwd=self.password, duration=self.duration)
        self.assertRaises(URLError, self.auth.authenticate, **kwargs)


class AWSAuthTestCase(BaseTestCase):
    host = 'sts.amazonaws.com'
    port = 443
    expected_url = ''.join([
        'Action=GetSessionToken',
        '&AWSAccessKeyId=12345678901234567890&DurationSeconds=3600',
        '&SignatureMethod=HmacSHA256&SignatureVersion=2&Version=2011-06-15',
        '&Timestamp={now}'.format(now=boto.utils.get_ts()),
        '&Signature=1234567890123456789012345678901234567890'
    ])
    auth = AWSAuthenticator(package=expected_url)

    def test_aws_authenticator(self):
        self.assertEqual(self.auth.host, self.host)
        self.assertEqual(self.auth.port, self.port)
        self.assertEqual(self.auth.package, self.expected_url)

    def test_aws_authentication_failure(self):
        import logging; logging.info("url = "+self.expected_url)
        try:
            self.auth.authenticate(timeout=1)
            self.assertFalse(True, msg="Auth should have thrown an exception")
        except (HTTPError, URLError):
            self.assertTrue(True, msg="Auth threw an exception, to be expected")


class UserTestCase(BaseTestCase):
    def test_unauthenticated_user(self):
        request = DummyRequest()
        user = User.get_auth_user(request)
        self.assertFalse(user.is_authenticated())

    def test_groupfinder_with_user_id(self):
        request = DummyRequest()
        groups = groupfinder(user_id='joe', request=request)
        self.assertEqual(groups, [Authenticated])

    def test_groupfinder_without_user_id(self):
        request = DummyRequest()
        groups = groupfinder(user_id=None, request=request)
        self.assertEqual(groups, [])


class ArbitraryRedirectTestCase(BaseTestCase):
    def test_redirect_with_extra_slash_in_scheme(self):
        unsafe_url = 'http:///www.example.com/'
        self.assertEqual(BaseView.sanitize_url(unsafe_url), '/')

    def test_path_redirect(self):
        url = 'http://www.example.com/foo/bar'
        self.assertEqual(BaseView.sanitize_url(url), '/foo/bar')

