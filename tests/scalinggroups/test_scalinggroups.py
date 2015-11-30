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
Scaling Group tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
import simplejson as json

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from boto.ec2.autoscale.tag import Tag

from eucaconsole.forms.scalinggroups import (
    BaseScalingGroupForm, ScalingGroupCreateForm, ScalingGroupEditForm, ScalingGroupDeleteForm,
    ScalingGroupPolicyCreateForm, ScalingGroupPolicyDeleteForm,
    ScalingGroupInstancesMarkUnhealthyForm, ScalingGroupInstancesTerminateForm)
from eucaconsole.i18n import _
from eucaconsole.views.dialogs import create_alarm_dialog
from eucaconsole.views.panels import form_field_row
from eucaconsole.views.scalinggroups import ScalingGroupsView, BaseScalingGroupView, ScalingGroupView

from tests import BaseViewTestCase, BaseFormTestCase, BaseTestCase


class ScalingGroupsViewTests(BaseViewTestCase):

    def test_landing_page_view(self):
        request = testing.DummyRequest()
        view = ScalingGroupsView(request)
        lpview = view.scalinggroups_landing()
        self.assertEqual(lpview.get('prefix'), '/scalinggroups')
        self.assertTrue('/scalinggroups/json' in lpview.get('json_items_endpoint'))  # JSON endpoint
        self.assertEqual(lpview.get('initial_sort_key'), 'name')
        filter_keys = lpview.get('filter_keys')
        self.assertTrue('availability_zones' in filter_keys)
        self.assertTrue('launch_config' in filter_keys)
        self.assertTrue('name' in filter_keys)
        self.assertTrue('placement_group' in filter_keys)


# Commenting these tests out since they don't even form proper request and rely on special
# logic to make test pass withtout valid connection. We need to get these tests working properly
# once moto is utlized more fully (based on Austin Summit discussion
#
#class ScalingGroupViewTests(BaseViewTestCase):
#
#    def test_is_base_scaling_group_view(self):
#        request = testing.DummyRequest()
#        view = ScalingGroupView(request)
#        self.assertTrue(isinstance(view, BaseScalingGroupView))
#
#    def test_missing_scaling_group_returns_404(self):
#        request = testing.DummyRequest()
#        self.assertRaises(HTTPNotFound, ScalingGroupView(request).scalinggroup_view)


class BaseScalingGroupFormTestCase(BaseFormTestCase):
    form_class = BaseScalingGroupForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('launch_config')
        self.assert_required('availability_zones')
        self.assert_not_required('load_balancers')
        self.assert_required('desired_capacity')
        self.assert_required('max_size')
        self.assert_required('min_size')
        self.assert_required('health_check_period')

    def test_launch_config_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.launch_config)
        self.assertTrue(hasattr(self.form.launch_config.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is None)


class ScalingGroupCreateFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupCreateForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('name')

    def test_name_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.name)
        self.assertTrue(hasattr(self.form.name.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is None)


class ScalingGroupEditFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupEditForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('default_cooldown')
        self.assert_required('termination_policies')

    def test_default_cooldown_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.default_cooldown)
        self.assertTrue(hasattr(self.form.default_cooldown.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is None)


class DeleteFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupDeleteForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')


class ScalingGroupPolicyCreateFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupPolicyCreateForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('name')
        self.assert_required('adjustment_direction')
        self.assert_required('adjustment_amount')
        self.assert_required('adjustment_type')
        self.assert_required('cooldown')
        self.assert_required('alarm')

    def test_name_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.name)
        self.assertTrue(hasattr(self.form.name.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is None)


class CreateAlarmDialogTestCase(BaseViewTestCase):
    request = testing.DummyRequest()

    def test_create_alarm_dialog(self):
        metric_unit_mapping = {'Latency': 'seconds'}
        dialog = create_alarm_dialog(None, self.request, metric_unit_mapping=metric_unit_mapping)
        controller_options = json.loads(dialog.get('controller_options_json'))
        self.assertEqual(controller_options.get('metric_unit_mapping'), metric_unit_mapping)


class ScalingGroupPolicyDeleteFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupPolicyDeleteForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')


class ScalingGroupInstancesMarkUnhealthyFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupInstancesMarkUnhealthyForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')


class ScalingGroupInstancesTerminateFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupInstancesTerminateForm
    request = testing.DummyRequest()
    request.session['region'] = 'dummy'

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_secure_form(self):
        self.has_field('csrf_token')


class BaseScalingGroupFormTestCaseWithVPCEnabledOnEucalpytus(BaseFormTestCase):
    form_class = BaseScalingGroupForm
    request = testing.DummyRequest()
    request.session.update({
        'cloud_type': 'euca',
        'supported_platforms': ['VPC'],
    })

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_scaling_group_form_vpc_network_choices_with_vpc_enabled_on_eucalyptus(self):
        self.assertFalse(('None', _(u'No VPC')) in self.form.vpc_network.choices)


class BaseScalingGroupFormTestCaseWithVPCDisabledOnEucalpytus(BaseFormTestCase):
    form_class = BaseScalingGroupForm
    request = testing.DummyRequest()
    request.session.update({
        'cloud_type': 'euca',
        'supported_platforms': [],
    })

    def setUp(self):
        self.form = self.form_class(self.request)

    def test_scaling_group_form_vpc_network_choices_with_vpc_disabled_on_eucalyptus(self):
        self.assertTrue(('None', _(u'No VPC')) in self.form.vpc_network.choices)

class ScalingGroupTagSaveTestCase(BaseTestCase):

    def setUp(self):
        self.orig_tags = [
            Tag(key='tag1', value='value1', propagate_at_launch=True),
            Tag(key='tag2', value='value2', propagate_at_launch=False),
            Tag(key='tag3', value='value3', propagate_at_launch=True),
        ]

    def test_autoscale_add_tags1(self):
        new_tags = self.orig_tags[:]
        (del_tags, update_tags) = ScalingGroupView.optimize_tag_update([], new_tags)
        self.assertTrue(len(del_tags) == 0)
        self.assertTrue(len(update_tags) == 3)

    def test_autoscale_add_tags2(self):
        new_tags = self.orig_tags[:]
        new_tags.append(
            Tag(key='tag4', value='value4', propagate_at_launch=True),
        )
        (del_tags, update_tags) = ScalingGroupView.optimize_tag_update(self.orig_tags, new_tags)
        self.assertTrue(len(del_tags) == 0)
        self.assertTrue(len(update_tags) == 1)

    def test_autoscale_delete_tags(self):
        new_tags = self.orig_tags[:-1]
        (del_tags, update_tags) = ScalingGroupView.optimize_tag_update(self.orig_tags, new_tags)
        self.assertTrue(len(del_tags) == 1)
        self.assertTrue(len(update_tags) == 0)

    def test_autoscale_modify_tags_1(self):
        new_tags = self.orig_tags[:]
        new_tags[1] = Tag(key='tag2', value='value2', propagate_at_launch=True)
        (del_tags, update_tags) = ScalingGroupView.optimize_tag_update(self.orig_tags, new_tags)
        self.assertTrue(len(del_tags) == 1)
        self.assertTrue(len(update_tags) == 1)

    def test_autoscale_modify_tags_2(self):
        new_tags = self.orig_tags[:]
        new_tags[1] = Tag(key='tag2', value='value4', propagate_at_launch=False)
        (del_tags, update_tags) = ScalingGroupView.optimize_tag_update(self.orig_tags, new_tags)
        self.assertTrue(len(del_tags) == 1)
        self.assertTrue(len(update_tags) == 1)

