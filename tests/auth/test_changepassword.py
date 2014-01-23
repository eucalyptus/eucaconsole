"""
Tests for change password forms

"""
from urllib2 import URLError

from pyramid.testing import DummyRequest

from koala.forms.login import EucaChangePasswordForm
from koala.models.auth import EucaAuthenticator
from tests import BaseTestCase, BaseFormTestCase


class EucaChangePasswordFormTestCase(BaseFormTestCase):
    form_class = EucaChangePasswordForm
    request = DummyRequest()

    def test_required_fields(self):
        self.assert_required('password')
        self.assert_required('new_password')
        self.assert_required('new_password2')

    def test_secure_form(self):
        self.has_field('csrf_token')


class EucaChangePasswordTestCase(BaseTestCase):
    host = 'unknown_host'
    duration = 3600
    auth = EucaAuthenticator(host=host, duration=duration)
    account = 'foo_account'
    username = 'foo'
    password = 'pw'
    new_password = 'newpass'

    def test_euca_authenticator(self):
        expected_url = ''.join([
            'https://{host}:8773/services/Tokens?Action=GetAccessToken'.format(host=self.host),
            '&DurationSeconds=3600&Version=2011-06-15'
        ])
        self.assertEqual(self.auth.auth_url, expected_url)

    def test_euca_authentication_failure(self):
        kwargs = dict(account=self.account, user=self.username, passwd=self.password,
                      new_passwd=self.new_password)
        self.assertRaises(URLError, self.auth.authenticate, **kwargs)

