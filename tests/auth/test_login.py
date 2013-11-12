"""
Tests for login forms

"""
from urllib2 import HTTPError, URLError

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


class AWSLoginFormTestCase(BaseFormTestCase):
    form_class = AWSLoginForm
    request = DummyRequest()

    def test_required_fields(self):
        self.assert_required('access_key')
        self.assert_required('secret_key')


class EucaAuthTestCase(BaseTestCase):
    host = 'unknown_host'
    duration = 3600
    auth = EucaAuthenticator(host=host, duration=duration)
    account = 'foo_account'
    username = 'foo'
    password = 'pw'

    def test_euca_authenticator(self):
        expected_url = ''.join([
            'https://{host}:8773/services/Tokens?Action=GetSessionToken'.format(host=self.host),
            '&DurationSeconds=3600&Version=2011-06-15'
        ])
        self.assertEqual(self.auth.auth_url, expected_url)

    def test_euca_authentication_failure(self):
        kwargs = dict(account=self.account, user=self.username, passwd=self.password)
        self.assertRaises(URLError, self.auth.authenticate, **kwargs)


class AWSAuthTestCase(BaseTestCase):
    access_key = 'foo_accesskey'
    secret_key = 'super-seekrit-key'
    endpoint = 'https://sts.amazonaws.com'
    auth = AWSAuthenticator(key_id=access_key, secret_key=secret_key, duration=3600)

    def test_aws_authenticator(self):
        self.assertEqual(self.auth.endpoint, self.endpoint)
        self.assertEqual(self.auth.host, 'sts.amazonaws.com')
        self.assertEqual(self.auth.parameters.get('AWSAccessKeyId'), self.access_key)
        self.assertEqual(self.auth.parameters.get('SignatureVersion'), 2)
        self.assertEqual(self.auth.parameters.get('SignatureMethod'), 'HmacSHA256')
        self.assertEqual(self.auth.parameters.get('Action'), 'GetSessionToken')
        self.assertEqual(self.auth.parameters.get('Version'), '2011-06-15')

    def test_aws_authentication_failure(self):
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
