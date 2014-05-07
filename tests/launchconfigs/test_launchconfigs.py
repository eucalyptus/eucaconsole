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
Launch Configuration tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing

from eucaconsole.forms import BaseSecureForm
from eucaconsole.forms.launchconfigs import CreateLaunchConfigForm
from eucaconsole.views.launchconfigs import LaunchConfigsView

from tests import BaseViewTestCase, BaseFormTestCase


class LaunchConfigViewTests(BaseViewTestCase):

    def test_view_defaults(self):
        request = testing.DummyRequest()
        view = LaunchConfigsView(request)
        self.assertEqual(view.prefix, '/launchconfigs')
        self.assertEqual(view.initial_sort_key, 'name')

    def test_fetching_items_without_connection(self):
        request = testing.DummyRequest()
        view = LaunchConfigsView(request)
        self.assertEqual(view.get_connection(), None)


class CreateLaunchConfigFormTestCase(BaseFormTestCase):
    form_class = CreateLaunchConfigForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_required_fields(self):
        self.assert_required('name')
        self.assert_required('instance_type')
        self.assert_required('securitygroup')


