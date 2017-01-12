# Copyright 2013-2016 Hewlett Packard Enterprise Development LP
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
VPC tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing

from eucaconsole.i18n import _
from eucaconsole.forms import BaseSecureForm
from eucaconsole.forms.vpcs import VPCForm, CreateVPCForm, SubnetForm

from tests import BaseFormTestCase


class VPCFormTestCase(BaseFormTestCase):
    """VPC details page form"""
    form_class = VPCForm
    request = testing.DummyRequest()

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_optional_fields(self):
        self.assert_not_required('name')
        self.assert_not_required('internet_gateway')


class CreateVPCFormTestCase(BaseFormTestCase):
    """Create VPC form tests"""
    form_class = CreateVPCForm
    request = testing.DummyRequest()

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_optional_fields(self):
        self.assert_not_required('name')
        self.assert_not_required('internet_gateway')

    def test_required_fields(self):
        self.assert_required('cidr_block')

    def test_invalid_cidr_block(self):
        cidr_block_input = self.form.cidr_block
        cidr_block_input.data = 'invalid CIDR block'
        self.form.validate()
        errors_list = self.form.get_errors_list()
        error = u'cidr_block: A valid CIDR block is required'
        self.assertIn(error, errors_list)


class SubnetFormTestCase(BaseFormTestCase):
    """Subnet details page form"""
    form_class = SubnetForm
    request = testing.DummyRequest()

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_optional_fields(self):
        self.assert_not_required('name')
        self.assert_not_required('route_table')

    def test_public_ip_auto_assignment_field(self):
        expected_choices = (
            ('true', _('Enabled')),
            ('false', _('Disabled')),
        )
        self.assertEqual(self.form.public_ip_auto_assignment.choices, expected_choices)
