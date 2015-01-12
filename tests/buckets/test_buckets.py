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
Tests for S3 buckets, objects, and related forms

"""
from boto.s3.bucket import Bucket
from boto.s3.key import Key

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest

from eucaconsole.forms.buckets import SharingPanelForm
from eucaconsole.views.buckets import BucketContentsView, BucketDetailsView

from tests import BaseFormTestCase, BaseViewTestCase


class BucketContentsViewTestCase(BaseViewTestCase):

    def test_get_unprefixed_key_name(self):
        request = testing.DummyRequest()
        view = BucketContentsView(request)
        prefixed_key = '/foo/bar/baz/bat.txt'
        unprefixed_key = view.get_unprefixed_key_name(prefixed_key)
        self.assertEqual(unprefixed_key, 'bat.txt')

    def test_generated_icon_class_for_file_types(self):
        request = testing.DummyRequest()
        view = BucketContentsView(request)
        self.assertEqual(view.get_icon_class('/foo/bar/baz.pdf'), 'fi-page-pdf')  # Test PDF
        self.assertEqual(view.get_icon_class('/foo/bar/baz.jpg'), 'fi-photo')  # Test image
        self.assertEqual(view.get_icon_class('/foo/bar/baz.txt'), 'fi-page')  # Test text file
        self.assertEqual(view.get_icon_class('/foo/bar/baz.zip'), 'fi-archive')  # Test zip file
        self.assertEqual(view.get_icon_class('/foo/bar/baz.unknown'), '')  # Test unknown

    def test_upload_page_returns_404_when_file_uploads_config_is_disabled(self):
        """File upload page should return a 404 when file.uploads.enabled is False"""
        request = testing.DummyRequest()
        request.registry.settings = {
            'file.uploads.enabled': 'false'
        }
        view = BucketContentsView(request).bucket_upload
        self.assertRaises(HTTPNotFound, view)

    def test_upload_post_returns_400_when_file_uploads_config_is_disabled(self):
        """File upload post handler should return a 400 when file.uploads.enabled is False"""
        request = testing.DummyRequest()
        request.registry.settings = {
            'file.uploads.enabled': 'false'
        }
        view = BucketContentsView(request).bucket_upload_post
        self.assertRaises(HTTPBadRequest, view)


class BucketDetailsViewTestCase(BaseViewTestCase):

    def test_versioning_update_action(self):
        request = testing.DummyRequest()
        view = BucketDetailsView(request)
        self.assertEqual(view.get_versioning_update_action('Disabled'), 'enable')
        self.assertEqual(view.get_versioning_update_action('Suspended'), 'enable')
        self.assertEqual(view.get_versioning_update_action('Enabled'), 'disable')


class SharingPanelFormTestCase(BaseFormTestCase):
    form_class = SharingPanelForm
    request = testing.DummyRequest()

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_acl_permission_choices_for_create_bucket(self):
        bucket = Bucket()
        form = self.form_class(self.request, bucket_object=bucket)
        permission_choices = dict(form.get_permission_choices())
        self.assertEqual(permission_choices.get('FULL_CONTROL'), 'Full Control')
        self.assertEqual(permission_choices.get('READ'), 'View/Download objects')
        self.assertEqual(permission_choices.get('WRITE'), 'Create/delete objects')

    def test_acl_permission_choices_for_object(self):
        key = Key()
        form = self.form_class(self.request, bucket_object=key)
        permission_choices = dict(form.get_permission_choices())
        self.assertEqual(permission_choices.get('FULL_CONTROL'), 'Full Control')
        self.assertEqual(permission_choices.get('READ'), 'Read-only')
        self.assertEqual(permission_choices.get('WRITE'), None)

