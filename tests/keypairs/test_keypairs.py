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
Key Pair tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing

from eucaconsole.forms.keypairs import KeyPairForm, KeyPairImportForm, KeyPairDeleteForm
from eucaconsole.views import BaseView
from eucaconsole.views.panels import form_field_row
from eucaconsole.views.keypairs import KeyPairsView, KeyPairView

from tests import BaseViewTestCase, BaseFormTestCase


class KeyPairsViewTests(BaseViewTestCase):
    request = testing.DummyRequest()
    view = KeyPairsView(request)

    def test_landing_page_view(self):
        lpview = self.view.keypairs_landing()
        self.assertEqual(lpview.get('prefix'), '/keypairs')
        self.assertTrue('/keypairs/json' in lpview.get('json_items_endpoint'))  # JSON endpoint
        self.assertEqual(lpview.get('initial_sort_key'), 'name')
        filter_keys = lpview.get('filter_keys')
        self.assertTrue('name' in filter_keys)
        self.assertTrue('fingerprint' in filter_keys)


class KeyPairViewTests(BaseViewTestCase):
    request = testing.DummyRequest()
    request.is_xhr = False
    view = KeyPairView(request)

    def test_is_base_view(self):
        self.assertTrue(isinstance(self.view, BaseView))

    def test_item_view(self):
        itemview = KeyPairView(self.request).keypair_view()
        self.assertEqual(itemview.get('keypair'), None)
        self.assertTrue(itemview.get('keypair_form') is not None)
        self.assertTrue(itemview.get('keypair_import_form') is not None)
        self.assertTrue(itemview.get('delete_form') is not None)
        self.assertTrue(itemview.get('keypair_created') is False)

    def test_keypair_create(self):
        createview = KeyPairView(self.request).keypair_create()
        self.assertTrue(createview is not None)


class KeyPairFormTestCase(BaseFormTestCase):
    form_class = KeyPairForm
    request = testing.DummyRequest()
    keypair = None
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('name')

    def test_field_validators(self):
        self.assert_min_length('name', 1)
        self.assert_max_length('name', 255)

    def test_name_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.name)
        self.assertTrue(hasattr(self.form.name.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is not None)


class KeyPairImportFormTestCase(BaseFormTestCase):
    form_class = KeyPairImportForm
    request = testing.DummyRequest()
    keypair = None
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('name')
        self.assert_required('key_material')

    def test_field_validators(self):
        self.assert_min_length('name', 1)
        self.assert_max_length('name', 255)
        self.assert_min_length('key_material', 1)

    def test_name_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.name)
        self.assertTrue(hasattr(self.form.name.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is not None)

    def test_key_material_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.key_material)
        self.assertTrue(hasattr(self.form.name.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength'), None)


class DeleteFormTestCase(BaseFormTestCase):
    form_class = KeyPairDeleteForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

