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
Image tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from eucaconsole.forms.images import ImageForm
from eucaconsole.views import TaggedItemView
from eucaconsole.views.images import ImagesView, ImageView

from tests import BaseViewTestCase, BaseFormTestCase


class ImagesViewTests(BaseViewTestCase):

    def test_landing_page_view(self):
        request = testing.DummyRequest()
        lpview = ImagesView(request).images_landing()
        self.assertEqual(lpview.get('prefix'), '/images')
        self.assertEqual(lpview.get('initial_sort_key'), 'name')
        filter_keys = lpview.get('filter_keys')
        self.assertTrue('architecture' in filter_keys)
        self.assertTrue('description' in filter_keys)
        self.assertTrue('id' in filter_keys)
        self.assertTrue('name' in filter_keys)
        self.assertTrue('owner_alias' in filter_keys)
        self.assertTrue('platform_name' in filter_keys)
        self.assertTrue('root_device_type' in filter_keys)
        self.assertTrue('tagged_name' in filter_keys)


class ImageViewTests(BaseViewTestCase):

    def test_is_tagged_item_view(self):
        request = testing.DummyRequest()
        view = ImageView(request)
        self.assertTrue(isinstance(view, TaggedItemView))

    def test_item_view(self):
        request = testing.DummyRequest()
        self.assertRaises(HTTPNotFound, ImageView(request).image_view)


class ImageFormTestCase(BaseFormTestCase):
    form_class = ImageForm
    request = testing.DummyRequest()
    image = None
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

