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
Security Group tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing

from eucaconsole.forms.securitygroups import SecurityGroupForm, SecurityGroupDeleteForm
from eucaconsole.views import TaggedItemView
from eucaconsole.views.panels import form_field_row
from eucaconsole.views.securitygroups import SecurityGroupsView, SecurityGroupView

from tests import BaseViewTestCase, BaseFormTestCase


class SecurityGroupsViewTests(BaseViewTestCase):

    def test_landing_page_view(self):
        request = testing.DummyRequest()
        lpview = SecurityGroupsView(request).securitygroups_landing()
        self.assertEqual(lpview.get('prefix'), '/securitygroups')
        self.assertEqual(lpview.get('initial_sort_key'), 'name')
        filter_keys = lpview.get('filter_keys')
        self.assertTrue('name' in filter_keys)
        self.assertTrue('description' in filter_keys)
        self.assertTrue('tags' in filter_keys)  # Object has tags


class SecurityGroupViewTests(BaseViewTestCase):
    request = testing.DummyRequest()
    view = SecurityGroupView(request)

    def test_is_tagged_view(self):
        """Security group view should inherit from TaggedItemView"""
        self.assertTrue(isinstance(self.view, TaggedItemView))

    def test_item_view(self):
        itemview = SecurityGroupView(self.request).securitygroup_view()
        self.assertEqual(itemview.get('security_group'), None)
        self.assertTrue(itemview.get('securitygroup_form') is not None)
        self.assertTrue(itemview.get('delete_form') is not None)

    def test_update_view(self):
        updateview = SecurityGroupView(self.request).securitygroup_update()
        self.assertEqual(updateview.get('security_group'), None)

    def test_delete_view(self):
        deleteview = SecurityGroupView(self.request).securitygroup_delete()
        self.assertTrue(deleteview is not None)


class SecurityGroupFormTestCase(BaseFormTestCase):
    form_class = SecurityGroupForm
    request = testing.DummyRequest()
    security_group = None
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('name')
        self.assert_required('description')

    def test_field_validators(self):
        self.assert_max_length('description', 255)

    def test_name_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.name)
        self.assertTrue(hasattr(self.form.name.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is None)

    def test_description_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.description)
        self.assertTrue(hasattr(self.form.name.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is not None)


class DeleteFormTestCase(BaseFormTestCase):
    form_class = SecurityGroupDeleteForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

