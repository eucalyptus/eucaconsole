"""
Tests for login forms

"""
from pyramid.testing import DummyRequest

from koala.forms.login import AWSLoginForm, EucaLoginForm
from koala.models.auth import AWSAuthenticator, EucaAuthenticator
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
    def test_euca_authenticator(self):
        host = 'localhost'
        duration = 3600
        auth = EucaAuthenticator(host=host, duration=duration)
        expected_url = ''.join([
            'https://localhost:8773/services/Tokens?Action=GetSessionToken',
            '&DurationSeconds=3600&Version=2011-06-15'
        ])
        self.assertEqual(auth.auth_url, expected_url)


class AWSAuthTestCase(BaseTestCase):
    def test_aws_authenticator(self):
        access_key = 'foo_accesskey'
        secret_key = 'super-seekrit-key'
        endpoint = 'https://sts.amazonaws.com'
        auth = AWSAuthenticator(key_id=access_key, secret_key=secret_key, duration=3600)
        self.assertEqual(auth.endpoint, endpoint)
        self.assertEqual(auth.host, 'sts.amazonaws.com')
        self.assertEqual(auth.parameters.get('AWSAccessKeyId'), access_key)
        self.assertEqual(auth.parameters.get('SignatureVersion'), 2)
        self.assertEqual(auth.parameters.get('SignatureMethod'), 'HmacSHA256')
        self.assertEqual(auth.parameters.get('Action'), 'GetSessionToken')
        self.assertEqual(auth.parameters.get('Version'), '2011-06-15')
