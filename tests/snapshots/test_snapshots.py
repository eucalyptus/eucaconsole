# Copyright 2013-2015 Hewlett Packard Enterprise Development LP
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Snapshots tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from boto.ec2 import connect_to_region
from moto import mock_ec2

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from eucaconsole.forms import BaseSecureForm
from eucaconsole.forms.snapshots import SnapshotForm, DeleteSnapshotForm
from eucaconsole.views import TaggedItemView, JSONResponse
from eucaconsole.views.snapshots import SnapshotsView, SnapshotView, SnapshotsJsonView

from tests import BaseViewTestCase, BaseFormTestCase


class MockSnapshotMixin(object):
    @staticmethod
    @mock_ec2
    def make_snapshot(volume=None, description='test snapshot description'):
        ec2_conn = connect_to_region('us-east-1')
        volume = volume or ec2_conn.create_volume(1, 'us-east-1a')
        snapshot = ec2_conn.create_snapshot(volume.id, description)
        return snapshot, ec2_conn


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
        request = testing.DummyRequest(post=True)
        view = SnapshotsJsonView(request).snapshots_json()
        self.assertEqual(view.__class__, JSONResponse)
        

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


class MockSnapshotViewTestCase(BaseViewTestCase, MockSnapshotMixin):

    @mock_ec2
    def test_snapshot_detail_view(self):
        snapshot, conn = self.make_snapshot()
        request = self.create_request(matchdict=dict(id=snapshot.id))
        view = SnapshotView(request, ec2_conn=conn).snapshot_view()
        view_snapshot = view.get('snapshot')
        self.assertEqual(view_snapshot.id, snapshot.id)
        self.assertEqual(view.get('snapshot_name'), snapshot.id)
        self.assertEqual(view.get('snapshot_description'), u'test snapshot description')
        self.assertEqual(view.get('exists_volume'), True)

