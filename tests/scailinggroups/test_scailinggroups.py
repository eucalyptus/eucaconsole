"""
Scaling Group tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from koala.forms.scalinggroups import (
    BaseScalingGroupForm, ScalingGroupCreateForm, ScalingGroupEditForm, ScalingGroupDeleteForm, ScalingGroupPolicyCreateForm, ScalingGroupPolicyDeleteForm, ScalingGroupInstancesMarkUnhealthyForm, ScalingGroupInstancesTerminateForm)
from koala.views import BaseView
from koala.views.panels import form_field_row
from koala.views.scalinggroups import ScalingGroupsView, BaseScalingGroupView, ScalingGroupView

from tests import BaseViewTestCase, BaseFormTestCase


class ScalingGroupsViewTests(BaseViewTestCase):
    request = testing.DummyRequest()
    view = ScalingGroupsView(request)

    def test_landing_page_view(self):
        lpview = self.view.scalinggroups_landing()
        self.assertEqual(lpview.get('prefix'), '/scalinggroups')
        self.assertTrue('/scalinggroups/json' in lpview.get('json_items_endpoint'))  # JSON endpoint
        self.assertEqual(lpview.get('initial_sort_key'), 'name')
        filter_keys = lpview.get('filter_keys')
        self.assertTrue('availability_zones' in filter_keys)
        self.assertTrue('launch_config' in filter_keys)
        self.assertTrue('name' in filter_keys)
        self.assertTrue('placement_group' in filter_keys)

class ScalingGroupViewTests(BaseViewTestCase):
    request = testing.DummyRequest()
    view = ScalingGroupView(request)

    def test_is_base_scaling_group_view(self):
        self.assertTrue(isinstance(self.view, BaseScalingGroupView))

    def test_item_view(self):
        itemview = ScalingGroupView(self.request).scalinggroup_view()
        self.assertEqual(itemview.get('scailing_group'), None)
        self.assertTrue(itemview.get('edit_form') is not None)
        self.assertTrue(itemview.get('delete_form') is not None)

class BaseScalingGroupFormTestCase(BaseFormTestCase):
    form_class = BaseScalingGroupForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('launch_config')
        self.assert_required('availability_zones')
        self.assert_required('desired_capacity')
        self.assert_required('max_size')
        self.assert_required('min_size')
        self.assert_required('health_check_type')
        self.assert_required('health_check_period')

    def test_field_validators(self):
        self.assert_min('desired_capacity', 0)
        self.assert_max('desired_capacity', 99)
        self.assert_min('max_size', 0)
        self.assert_max('max_size', 99)
        self.assert_min('min_size', 0)
        self.assert_max('min_size', 99)

    def test_launch_config_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.launch_config)
        self.assertTrue(hasattr(self.form.launch_config.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is None)

class ScalingGroupCreateFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupCreateForm
    request = testing.DummyRequest()
    form = form_class(request)

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
    form = form_class(request)

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
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token');

class ScalingGroupPolicyCreateFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupPolicyCreateForm
    request = testing.DummyRequest()
    form = form_class(request)

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

class ScalingGroupPolicyDeleteFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupPolicyDeleteForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token');

class ScalingGroupInstancesMarkUnhealthyFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupInstancesMarkUnhealthyForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token');

class ScalingGroupInstancesTerminateFormTestCase(BaseFormTestCase):
    form_class = ScalingGroupInstancesTerminateForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token');

