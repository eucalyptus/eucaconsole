"""
Snapshots tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from koala.forms import BaseSecureForm
from koala.forms.snapshots import SnapshotForm, DeleteSnapshotForm
from koala.views import TaggedItemView
from koala.views.snapshots import SnapshotsView, SnapshotView

from tests import BaseViewTestCase, BaseFormTestCase


class SnapshotsViewTests(BaseViewTestCase):
    """Snapshots landing page view"""
    def test_snapshots_view_defaults(self):
        request = testing.DummyRequest()
        view = SnapshotsView(request)
        self.assertEqual(view.prefix, '/snapshots')
        self.assertEqual(view.initial_sort_key, '-start_time')

    def test_snapshots_landing_page(self):
        request = testing.DummyRequest()
        view = SnapshotsView(request).snapshots_landing()
        self.assertTrue('/snapshots/json' in view.get('json_items_endpoint'))

    def test_snapshots_landing_page_json(self):
        request = testing.DummyRequest()
        view = SnapshotsView(request).snapshots_json()
        self.assertEqual(view.get('results'), [])


class SnapshotViewTests(BaseViewTestCase):
    """Snapshot detail page view"""

    def test_is_tagged_view(self):
        """Snapshot view should inherit from TaggedItemView"""
        request = testing.DummyRequest()
        view = SnapshotView(request)
        self.assertTrue(isinstance(view, TaggedItemView))

    def test_missing_snapshot_view(self):
        """Snapshot view should return 404 for missing snapshot"""
        request = testing.DummyRequest()
        view = SnapshotView(request).snapshot_view
        self.assertRaises(HTTPNotFound, view)

    def test_missing_snapshot_none(self):
        """Snapshot view should return 404 for missing snapshot"""
        request = testing.DummyRequest()
        snapshot = SnapshotView(request).get_snapshot()
        self.assertTrue(snapshot is None)

    def test_snapshot_update_view(self):
        """Snapshot update should contain the snapshot form"""
        request = testing.DummyRequest(post=True)
        view = SnapshotView(request).snapshot_update()
        self.assertTrue(view.get('snapshot_form') is not None)


class SnapshotUpdateFormTestCase(BaseFormTestCase):
    """Update Snapshot form on snapshot page"""
    form_class = SnapshotForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_required_fields(self):
        self.assert_required('volume_id')

    def test_optional_fields(self):
        self.assert_not_required('name')
        self.assert_not_required('description')


class SnapshotDeleteFormTestCase(BaseFormTestCase):
    """Delete snapshot form on snapshot page"""
    form_class = DeleteSnapshotForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

