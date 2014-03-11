"""
Launch Configuration tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing

from eucaconsole.forms import BaseSecureForm
from eucaconsole.forms.launchconfigs import CreateLaunchConfigForm
from eucaconsole.views.launchconfigs import LaunchConfigsView

from tests import BaseViewTestCase, BaseFormTestCase


class LaunchConfigViewTests(BaseViewTestCase):

    def test_view_defaults(self):
        request = testing.DummyRequest()
        view = LaunchConfigsView(request)
        self.assertEqual(view.prefix, '/launchconfigs')
        self.assertEqual(view.initial_sort_key, 'name')

    def test_fetching_items_without_connection(self):
        request = testing.DummyRequest()
        view = LaunchConfigsView(request)
        self.assertEqual(view.get_connection(), None)


class CreateLaunchConfigFormTestCase(BaseFormTestCase):
    form_class = CreateLaunchConfigForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_required_fields(self):
        self.assert_required('name')
        self.assert_required('instance_type')
        self.assert_required('securitygroup')


