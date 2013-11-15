"""
Launch Configuration tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing

from koala.views.launchconfigs import LaunchConfigsView
from tests import BaseViewTestCase


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
        self.assertEqual(view.get_items(), [])  # empty since there's no connection

