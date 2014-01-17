"""
Volumes tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from koala.forms import BaseSecureForm
from koala.forms.volumes import (
    VolumeForm, DeleteVolumeForm, CreateSnapshotForm, DeleteSnapshotForm, AttachForm, DetachForm)
from koala.views import TaggedItemView
from koala.views.volumes import VolumesView, VolumeView

from tests import BaseViewTestCase, BaseFormTestCase


class VolumesViewTests(BaseViewTestCase):
    """Volumes landing page view"""
    def test_volumes_view_defaults(self):
        request = testing.DummyRequest()
        view = VolumesView(request)
        self.assertEqual(view.prefix, '/volumes')
        self.assertEqual(view.initial_sort_key, '-create_time')

    def test_volumes_landing_page(self):
        request = testing.DummyRequest()
        view = VolumesView(request).volumes_landing()
        self.assertIn('/volumes/json', view.get('json_items_endpoint'))

    def test_volumes_landing_page_json(self):
        request = testing.DummyRequest()
        view = VolumesView(request).volumes_json()
        self.assertEqual(view.get('results'), [])


class VolumeViewTests(BaseViewTestCase):
    """Volume detail page view"""

    def test_is_tagged_view(self):
        """Volume view should inherit from TaggedItemView"""
        request = testing.DummyRequest()
        view = VolumeView(request)
        self.assertTrue(isinstance(view, TaggedItemView))

    def test_missing_volume_view(self):
        """Volume view should return 404 for missing volume"""
        request = testing.DummyRequest()
        view = VolumeView(request).volume_view
        self.assertRaises(HTTPNotFound, view)

    def test_volume_update_view(self):
        """Volume update should contain the volume form"""
        request = testing.DummyRequest(post=True)
        view = VolumeView(request).volume_update()
        self.assertIsNotNone(view.get('volume_form'))


class VolumeUpdateFormTestCase(BaseFormTestCase):
    """Update Volume form on volume page"""
    form_class = VolumeForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_required_fields(self):
        self.assert_required('size')
        self.assert_required('zone')

    def test_optional_fields(self):
        self.assert_not_required('name')
        self.assert_not_required('snapshot_id')


class VolumeDeleteFormTestCase(BaseFormTestCase):
    """Delete volume form on volume page"""
    form_class = DeleteVolumeForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class VolumeAttachFormTestCase(BaseFormTestCase):
    """Attach Volume form on volume page"""
    form_class = AttachForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_required_fields(self):
        self.assert_required('instance_id')
        self.assert_required('device')


class VolumeDetachFormTestCase(BaseFormTestCase):
    """Detach Volume form on volume page"""
    form_class = DetachForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class VolumeCreateSnapshotFormTestCase(BaseFormTestCase):
    """Create snapshot form on volume page"""
    form_class = CreateSnapshotForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_optional_fields(self):
        self.assert_not_required('description')

    def test_description_maxlength(self):
        self.assert_max_length('description', 255)


class VolumeDeleteSnapshotFormTestCase(BaseFormTestCase):
    """Delete snapshot form on volume page"""
    form_class = DeleteSnapshotForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))
