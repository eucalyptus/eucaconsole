"""
Image tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from koala.forms.images import ImageForm
from koala.views import TaggedItemView
from koala.views.panels import form_field_row
from koala.views.images import ImagesView, ImageView

from tests import BaseViewTestCase, BaseFormTestCase


class ImagesViewTests(BaseViewTestCase):
    request = testing.DummyRequest()
    view = ImagesView(request)

    def test_landing_page_view(self):
        lpview = self.view.images_landing()
        self.assertEqual(lpview.get('prefix'), '/images')
        self.assertTrue('/images/json' in lpview.get('json_items_endpoint'))  # JSON endpoint
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
    request = testing.DummyRequest()
    view = ImageView(request)

    def test_is_tagged_item_view(self):
        self.assertTrue(isinstance(self.view, TaggedItemView))

    def test_item_view(self):
        itemview = ImageView(self.request).image_view()
        self.assertEqual(itemview.get('image'), None)
        self.assertTrue(itemview.get('image_display_name') is None)
        self.assertTrue(itemview.get('image_form') is not None)

    def test_image_update(self):
        itemview = ImageView(self.request).image_view()
        self.assertEqual(itemview.get('image'), None)
        self.assertTrue(itemview.get('image_display_name') is None)
        self.assertTrue(itemview.get('image_form') is not None)

class ImageFormTestCase(BaseFormTestCase):
    form_class = ImageForm
    request = testing.DummyRequest()
    image = None
    form = form_class(request)

    def test_secure_form(self):
        self.has_field('csrf_token')

