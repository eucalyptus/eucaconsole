"""
Instances tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from eucaconsole.forms import BaseSecureForm
from eucaconsole.forms.instances import StartInstanceForm, StopInstanceForm, RebootInstanceForm, TerminateInstanceForm
from eucaconsole.forms.instances import AttachVolumeForm, DetachVolumeForm, LaunchInstanceForm
from eucaconsole.views import TaggedItemView
from eucaconsole.views.instances import InstancesView, InstancesJsonView, InstanceView

from tests import BaseViewTestCase, BaseFormTestCase


class InstancesViewTests(BaseViewTestCase):
    """Instances landing page view"""
    def test_instances_view_defaults(self):
        request = testing.DummyRequest()
        view = InstancesView(request)
        self.assertEqual(view.prefix, '/instances')
        self.assertEqual(view.initial_sort_key, '-launch_time')

    def test_instances_landing_page(self):
        request = testing.DummyRequest()
        view = InstancesView(request).instances_landing()
        self.assertTrue('/instances/json' in view.get('json_items_endpoint'))


class InstanceViewTests(BaseViewTestCase):
    """Instance detail page view"""

    def test_is_tagged_view(self):
        """Instance view should inherit from TaggedItemView"""
        request = testing.DummyRequest()
        view = InstanceView(request)
        self.assertTrue(isinstance(view, TaggedItemView))

    def test_missing_instance_view(self):
        """Instance view should return 404 for missing instance"""
        request = testing.DummyRequest()
        view = InstanceView(request).instance_view
        self.assertRaises(HTTPNotFound, view)

    def test_instance_update_view(self):
        """Instance update should contain the instance form"""
        request = testing.DummyRequest(post=True)
        view = InstanceView(request).instance_update()
        self.assertTrue(view.get('instance_form') is not None)


class InstanceStartFormTestCase(BaseFormTestCase):
    form_class = StartInstanceForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceStopFormTestCase(BaseFormTestCase):
    form_class = StopInstanceForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceRebootFormTestCase(BaseFormTestCase):
    form_class = RebootInstanceForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceTerminateFormTestCase(BaseFormTestCase):
    form_class = TerminateInstanceForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceAttachVolumeFormTestCase(BaseFormTestCase):
    """Attach Volume form on instance page"""
    form_class = AttachVolumeForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_required_fields(self):
        self.assert_required('volume_id')
        self.assert_required('device')


class InstanceDetachVolumeFormTestCase(BaseFormTestCase):
    """Detach Volume form on instance page"""
    form_class = DetachVolumeForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceLaunchFormTestCase(BaseFormTestCase):
    form_class = LaunchInstanceForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_required_fields(self):
        self.assert_required('number')
        self.assert_required('instance_type')
        self.assert_required('securitygroup')

