"""
Image tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing

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

