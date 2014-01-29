"""
IP Address tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from koala.forms.ipaddresses import AllocateIPsForm, AssociateIPForm, DisassociateIPForm, ReleaseIPForm
from koala.views import BaseView
from koala.views.panels import form_field_row
from koala.views.ipaddresses import IPAddressesView, IPAddressView

from tests import BaseViewTestCase, BaseFormTestCase


class IPAddressesViewTests(BaseViewTestCase):

    def test_landing_page_view(self):
        request = testing.DummyRequest()
        view = IPAddressesView(request)
        lpview = view.ipaddresses_landing()
        self.assertEqual(lpview.get('prefix'), '/ipaddresses')
        self.assertTrue('/ipaddresses/json' in lpview.get('json_items_endpoint'))  # JSON endpoint
        self.assertEqual(lpview.get('initial_sort_key'), 'public_ip')
        filter_keys = lpview.get('filter_keys')
        self.assertTrue('public_ip' in filter_keys)
        self.assertTrue('instance_id' in filter_keys)

class IPAddressTests(BaseViewTestCase):
    request = testing.DummyRequest()
    view = IPAddressView(request)

    def test_is_base_view(self):
        self.assertTrue(isinstance(self.view, BaseView))

    def test_item_view(self):
        itemview = IPAddressView(self.request).ipaddress_view()
        self.assertEqual(itemview.get('eip'), None)
        self.assertTrue(itemview.get('associate_form') is not None)
        self.assertTrue(itemview.get('disassociate_form') is not None)
        self.assertTrue(itemview.get('release_form') is not None)

class AllocateIPsFormTestCase(BaseFormTestCase):
    form_class = AllocateIPsForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('ipcount')

    def test_ipcount_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.ipcount)
        self.assertTrue(hasattr(self.form.ipcount.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is None)

class AssociateIPFormTestCase(BaseFormTestCase):
    form_class = AssociateIPForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

    def test_required_fields(self):
        self.assert_required('instance_id')

    def test_instand_id_field_html_attrs(self):
        """Test if required fields pass the proper HTML attributes to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.instance_id)
        self.assertTrue(hasattr(self.form.instance_id.flags, 'required'))
        self.assertTrue('required' in fieldrow.get('html_attrs').keys())
        self.assertTrue(fieldrow.get('html_attrs').get('maxlength') is None)

class DisassociateIPFormTestCase(BaseFormTestCase):
    form_class = DisassociateIPForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

class ReleaseIPFormTestCase(BaseFormTestCase):
    form_class = ReleaseIPForm
    request = testing.DummyRequest()
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

