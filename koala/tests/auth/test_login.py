"""
Tests for login forms

"""
from pyramid.testing import DummyRequest

from koala.forms.login import EucaLoginForm
from koala.tests import BaseFormTestCase


class EucaLoginFormTestCase(BaseFormTestCase):
    form_class = EucaLoginForm
    request = DummyRequest()

    def test_required_fields(self):
        self.assert_required('account')
        self.assert_required('username')
        self.assert_required('password')

    def test_valid_form(self):
        form = EucaLoginForm(
            request=self.request,
            data=dict(account='foo', username='bar', password='baz')
        )
        self.assertEqual(form.errors, {})
