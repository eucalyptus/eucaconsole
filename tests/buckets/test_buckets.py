# -*- coding: utf-8 -*-
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
Tests for S3 buckets, objects, and related forms

"""
import re

import boto

from boto.s3.acl import ACL, Policy
from boto.s3.bucket import Bucket
from boto.s3.key import Key
from boto.s3.user import User
from moto import mock_s3

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest

from eucaconsole.forms.buckets import SharingPanelForm
from eucaconsole.views.buckets import (
    BucketContentsView, BucketContentsJsonView, BucketDetailsView, BucketItemDetailsView, BucketXHRView,
    FOLDER_NAME_PATTERN
)

from tests import BaseFormTestCase, BaseViewTestCase, BaseTestCase


class MockBucketMixin(object):
    @staticmethod
    @mock_s3
    def make_bucket(name='test_bucket', policy=None, owner_id=None):
        s3_conn = boto.connect_s3()
        policy = policy or Policy()
        owner_id = owner_id or 'test_owner_id'
        policy.owner = User(id=owner_id)
        acl = ACL()
        acl.grants = []
        policy.acl = acl
        bucket = s3_conn.create_bucket(name)
        bucket.policy = policy
        return bucket, policy


class BucketMixinTestCase(BaseViewTestCase):

    def test_subpath_fixes(self):
        request = testing.DummyRequest()
        request.environ = {'PATH_INFO': "some/path//with/extra/slash"}
        request.subpath = ('some', 'path', 'with', 'extra', 'slash')
        request.matchdict['name'] = 'bucket'
        view = BucketXHRView(request)
        new_subpath = view.get_subpath('bucket')
        self.assertEqual(request.environ['PATH_INFO'], "/".join(new_subpath))


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


class MockBucketDetailsViewTestCase(BaseViewTestCase, MockBucketMixin):

    @mock_s3
    def test_bucket_details_view_without_versioning(self):
        request = self.create_request()
        bucket, bucket_acl = self.make_bucket()
        view = BucketDetailsView(request, bucket=bucket, bucket_acl=bucket_acl).bucket_details()
        self.assertEqual(view.get('bucket_name'), 'test_bucket')
        self.assertEqual(view.get('bucket_contents_url'), '/buckets/test_bucket/contents/')
        self.assertEqual(view.get('versioning_status'), 'Disabled')
        self.assertEqual(view.get('update_versioning_action'), 'enable')

    @mock_s3
    def test_bucket_details_view_with_versioning(self):
        request = self.create_request()
        bucket, bucket_acl = self.make_bucket()
        bucket.configure_versioning(True)
        view = BucketDetailsView(request, bucket=bucket, bucket_acl=bucket_acl).bucket_details()
        self.assertEqual(view.get('bucket_name'), 'test_bucket')
        self.assertEqual(view.get('bucket_contents_url'), '/buckets/test_bucket/contents/')
        self.assertEqual(view.get('versioning_status'), 'Enabled')
        self.assertEqual(view.get('update_versioning_action'), 'disable')


class MockBucketContentsJsonViewTestCase(BaseViewTestCase, MockBucketMixin):

    @mock_s3
    def test_bucket_contents_json_view_with_file(self):
        bucket, bucket_acl = self.make_bucket()
        bucket.new_key("/file-one").set_contents_from_string('file content')
        request = self.create_request(matchdict=dict(name=bucket.name))
        view = BucketContentsJsonView(request, bucket=bucket)
        bucket_contents_json_view = view.bucket_contents_json()
        results = bucket_contents_json_view.get('results')
        self.assertEqual(len(results), 1)
        item = results[0]
        self.assertEqual(item.get('details_url'), '/buckets/test_bucket/itemdetails/file-one')
        self.assertEqual(item.get('full_key_name'), 'file-one')
        self.assertEqual(item.get('is_folder'), False)

    @mock_s3
    def test_bucket_contents_json_view_with_folder(self):
        bucket, bucket_acl = self.make_bucket()
        bucket.new_key("/folder-one/").set_contents_from_string('')
        request = self.create_request(matchdict=dict(name=bucket.name))
        view = BucketContentsJsonView(request, bucket=bucket)
        bucket_contents_json_view = view.bucket_contents_json()
        results = bucket_contents_json_view.get('results')
        self.assertEqual(len(results), 1)
        item = results[0]
        self.assertEqual(item.get('details_url'), '/buckets/test_bucket/itemdetails/folder-one/')
        self.assertEqual(item.get('full_key_name'), 'folder-one/')
        self.assertEqual(item.get('is_folder'), True)
        self.assertEqual(item.get('icon'), 'fi-folder')
        self.assertEqual(item.get('size'), 0)
        self.assertEqual(item.get('download_url'), '')


class MockBucketContentsViewTestCase(BaseViewTestCase, MockBucketMixin):

    @mock_s3
    def test_bucket_contents_view_with_bucket(self):
        bucket, bucket_acl = self.make_bucket()
        request = self.create_request(matchdict=dict(name=bucket.name))
        view = BucketContentsView(request, bucket_name=bucket.name).bucket_contents()
        self.assertEqual(view.get('display_path'), 'test_bucket')

    @mock_s3
    def test_bucket_contents_view_with_folder(self):
        bucket, bucket_acl = self.make_bucket()
        bucket.new_key("/folder-one/").set_contents_from_string('')
        request = self.create_request(matchdict=dict(name=bucket.name))
        request.environ = {'PATH_INFO': u'test_bucket/folder-one'}
        request.subpath = ('folder-one', )
        view = BucketContentsView(request, bucket=bucket).bucket_contents()
        self.assertEqual(view.get('display_path'), 'folder-one')


class MockObjectDetailsViewTestCase(BaseViewTestCase, MockBucketMixin):

    @mock_s3
    def test_object_details_view(self):
        request = self.create_request()
        path = '/buckets/test_bucket/itemdetails/'
        file_name = 'file-two'
        file_content = 'file two content'
        request.path = path
        request.subpath = (file_name, )
        request.environ = {'PATH_INFO': u'{0}/{1}'.format(path, file_name)}
        bucket, bucket_acl = self.make_bucket()
        bucket.new_key(u'/{0}'.format(file_name)).set_contents_from_string(file_content)
        view = BucketItemDetailsView(request, bucket=bucket, bucket_item_acl=bucket_acl).bucket_item_details()
        item = view.get('bucket_item')
        self.assertEqual(item.bucket.name, 'test_bucket')
        self.assertEqual(int(item.content_length), len(file_content))
        self.assertEqual(item.content_type, 'application/octet-stream')
        self.assertEqual(item.etag, '"257075e03fc5351067247f7e04f8c74f"')
        self.assertEqual(item.content_md5, 'JXB14D/FNRBnJH9+BPjHTw==')


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


class CreateS3FolderTestCase(BaseTestCase):

    def test_valid_s3_folder_names(self):
        valid_pattern = FOLDER_NAME_PATTERN
        matches = (
            (u'folder123', True),
            (u'folderÅ', True),
            (u'folder/123', False),
        )
        for pattern, valid in matches:
            self.assertEqual(bool(re.match(valid_pattern, pattern)), valid)
