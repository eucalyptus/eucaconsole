"""
Tests for change password forms

"""
from urllib2 import URLError

from pyramid.testing import DummyRequest

from eucaconsole.forms.login import EucaChangePasswordForm
from eucaconsole.models.auth import EucaAuthenticator
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
    port = 8773
    auth = EucaAuthenticator(host=host, port=port)
    account = 'foo_account'
    username = 'foo'
    password = 'pw'
    new_password = 'newpass'
    duration = 3600


    def test_euca_authentication_failure(self):
        kwargs = dict(account=self.account, user=self.username, passwd=self.password,
                      new_passwd=self.new_password, duration=self.duration)
        self.assertRaises(URLError, self.auth.authenticate, **kwargs)

