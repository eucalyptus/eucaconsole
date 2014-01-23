"""
Tests for login forms

"""
from urllib2 import HTTPError, URLError

import boto
from pyramid.security import Authenticated
from pyramid.testing import DummyRequest

from koala.forms.login import AWSLoginForm, EucaLoginForm
from koala.models.auth import AWSAuthenticator, EucaAuthenticator, User, groupfinder
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
    duration = 3600
    auth = EucaAuthenticator(host=host, duration=duration)
    account = 'foo_account'
    username = 'foo'
    password = 'pw'

    def test_euca_authenticator(self):
        expected_url = ''.join([
            'https://{host}:8773/services/Tokens?Action=GetAccessToken'.format(host=self.host),
            '&DurationSeconds=3600&Version=2011-06-15'
        ])
        self.assertEqual(self.auth.auth_url, expected_url)

    def test_euca_authentication_failure(self):
        kwargs = dict(account=self.account, user=self.username, passwd=self.password)
        self.assertRaises(URLError, self.auth.authenticate, **kwargs)


class AWSAuthTestCase(BaseTestCase):
    endpoint = 'https://sts.amazonaws.com'
    expected_url = ''.join([
        'Action=GetSessionToken',
        '&AWSAccessKeyId=12345678901234567890&DurationSeconds=3600',
        '&SignatureMethod=HmacSHA256&SignatureVersion=2&Version=2011-06-15',
        '&Timestamp={now}'.format(now=boto.utils.get_ts()),
        '&Signature=1234567890123456789012345678901234567890'
    ])
    auth = AWSAuthenticator(package=expected_url)

    def test_aws_authenticator(self):
        self.assertEqual(self.auth.endpoint, self.endpoint)
        self.assertEqual(self.auth.package, self.expected_url)

    def test_aws_authentication_failure(self):
        import logging; logging.info("url = "+self.expected_url)
        self.assertRaises(HTTPError, self.auth.authenticate, timeout=1)


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
