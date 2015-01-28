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
Instances tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from eucaconsole.forms import BaseSecureForm
from eucaconsole.forms.instances import (
    StartInstanceForm, StopInstanceForm, RebootInstanceForm, TerminateInstanceForm,
    AttachVolumeForm, DetachVolumeForm, LaunchInstanceForm, InstanceCreateImageForm,
    InstancesFiltersForm
)
from eucaconsole.i18n import _
from eucaconsole.views import TaggedItemView
from eucaconsole.views.instances import InstancesView, InstanceView

from tests import BaseViewTestCase, BaseFormTestCase, Mock


class InstancesViewTests(BaseViewTestCase):
    """Instances landing page view"""
    def test_instances_view_defaults(self):
        request = testing.DummyRequest()
        view = InstancesView(request)
        self.assertEqual(view.prefix, '/instances')
        self.assertEqual(view.initial_sort_key, '-launch_time')

    def test_instances_landing_page(self):
        request = testing.DummyRequest()
        request.session['cloud_type'] = 'none'
        request.session['role_access'] = True
        view = InstancesView(request).instances_landing()
        self.assertTrue('/instances/json' in view.get('json_items_endpoint'))


class InstanceViewTests(BaseViewTestCase):
    """Instance detail page view"""

    def test_is_tagged_view(self):
        """Instance view should inherit from TaggedItemView"""
        request = testing.DummyRequest()
        request.session['cloud_type'] = 'none'
        request.session['role_access'] = True
        view = InstanceView(request)
        self.assertTrue(isinstance(view, TaggedItemView))

    def test_missing_instance_view(self):
        """Instance view should return 404 for missing instance"""
        request = testing.DummyRequest()
        request.session['cloud_type'] = 'none'
        request.session['role_access'] = True
        view = InstanceView(request).instance_view
        self.assertRaises(HTTPNotFound, view)

    def test_instance_update_view(self):
        """Instance update should contain the instance form"""
        request = testing.DummyRequest(post=True)
        request.session['cloud_type'] = 'none'
        request.session['role_access'] = True
        view = InstanceView(request).instance_update()
        self.assertTrue(view.get('instance_form') is not None)


class InstanceStartFormTestCase(BaseFormTestCase):
    form_class = StartInstanceForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceStopFormTestCase(BaseFormTestCase):
    form_class = StopInstanceForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceRebootFormTestCase(BaseFormTestCase):
    form_class = RebootInstanceForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceTerminateFormTestCase(BaseFormTestCase):
    form_class = TerminateInstanceForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceAttachVolumeFormTestCase(BaseFormTestCase):
    """Attach Volume form on instance page"""
    form_class = AttachVolumeForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_required_fields(self):
        self.assert_required('volume_id')
        self.assert_required('device')


class AttachVolumeDeviceEucalyptusTestCase(BaseFormTestCase):
    form_class = AttachVolumeForm
    request = testing.DummyRequest()
    request.session['cloud_type'] = 'euca'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_initial_attach_device_on_eucalyptus(self):
        instance = Mock()
        instance.block_device_mapping = {}
        device = self.form_class.suggest_next_device_name(self.request, instance)
        self.assertEqual(device, '/dev/vdc')

    def test_next_attach_device_on_eucalyptus(self):
        instance = Mock()
        instance.block_device_mapping = {'/dev/vdc': 'foo'}
        device = self.form_class.suggest_next_device_name(self.request, instance)
        self.assertEqual(device, '/dev/vdd')


class AttachVolumeDeviceAWSTestCase(BaseFormTestCase):
    form_class = AttachVolumeForm
    request = testing.DummyRequest()
    request.session['cloud_type'] = 'aws'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_initial_attach_device_on_aws(self):
        instance = Mock()
        instance.block_device_mapping = {}
        device = self.form_class.suggest_next_device_name(self.request, instance)
        self.assertEqual(device, '/dev/sdf')

    def test_next_attach_device_on_aws(self):
        instance = Mock()
        instance.block_device_mapping = {'/dev/sdf': 'foo'}
        device = self.form_class.suggest_next_device_name(self.request, instance)
        self.assertEqual(device, '/dev/sdg')


class InstanceDetachVolumeFormTestCase(BaseFormTestCase):
    """Detach Volume form on instance page"""
    form_class = DetachVolumeForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))


class InstanceLaunchFormTestCase(BaseFormTestCase):
    form_class = LaunchInstanceForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_required_fields(self):
        self.assert_required('number')
        self.assert_required('instance_type')
        self.assert_required('securitygroup')


class InstanceCreateImageFormTestCase(BaseFormTestCase):
    form_class = InstanceCreateImageForm

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_required_fields(self):
        self.assert_required('name')
        self.assert_required('s3_bucket')
        self.assert_required('s3_prefix')

    def test_deprecated_required_validator(self):
        """Test usage of deprecated validator.Required"""
        try:
            from wtforms.validators import Required
            for name, field in self.form._fields.items():
                validator = self.get_validator(name, Required)
                if isinstance(validator, Required):
                    assert False
        except ImportError:
            pass


class InstanceLaunchFormTestCaseWithVPCEnabledOnEucalpytus(BaseFormTestCase):
    form_class = LaunchInstanceForm
    request = testing.DummyRequest()
    request.session.update({
        'cloud_type': 'euca',
        'supported_platforms': ['VPC'],
    })

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_launch_instance_form_vpc_network_choices_with_vpc_enabled_on_eucalyptus(self):
        self.assertFalse(('None', _(u'No VPC')) in self.form.vpc_network.choices)


class InstanceLaunchFormTestCaseWithVPCDisabledOnEucalpytus(BaseFormTestCase):
    form_class = LaunchInstanceForm
    request = testing.DummyRequest()
    request.session.update({
        'cloud_type': 'euca',
        'supported_platforms': [],
    })

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_launch_instance_form_vpc_network_choices_with_vpc_disabled_on_eucalyptus(self):
        self.assertTrue(('None', _(u'No VPC')) in self.form.vpc_network.choices)


class InstancesFiltersFormTestCaseOnAWS(BaseFormTestCase):
    form_class = InstancesFiltersForm
    request = testing.DummyRequest()

    def setUp(self):
        self.form = self.form_class(self.request, cloud_type='aws')

    def test_instances_filters_form_vpc_id_choices_on_aws(self):
        self.assertTrue(('None', _(u'No VPC')) in self.form.vpc_id.choices)
