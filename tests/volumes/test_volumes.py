# Copyright 2013-2014 Eucalyptus Systems, Inc.
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
Volumes tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from eucaconsole.forms import BaseSecureForm
from eucaconsole.forms.volumes import (
    VolumeForm, DeleteVolumeForm, CreateSnapshotForm, DeleteSnapshotForm, AttachForm, DetachForm)
from eucaconsole.views import TaggedItemView
from eucaconsole.views.volumes import VolumesView, VolumesJsonView, VolumeView

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
        self.assertTrue('/volumes/json' in view.get('json_items_endpoint'))


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
        self.assertTrue(view.get('volume_form') is not None)


class VolumeUpdateFormTestCase(BaseFormTestCase):
    """Update Volume form on volume page"""
    form_class = VolumeForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

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
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class VolumeAttachFormTestCase(BaseFormTestCase):
    """Attach Volume form on volume page"""
    form_class = AttachForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

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
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class VolumeCreateSnapshotFormTestCase(BaseFormTestCase):
    """Create snapshot form on volume page"""
    form_class = CreateSnapshotForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

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
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))
