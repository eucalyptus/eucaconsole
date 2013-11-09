"""
Instances tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing

from koala.tests import BaseLiveTestCase


class InstancesViewTests(BaseLiveTestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_instances_view_defaults(self):
        from koala.views.instances import InstancesView
        request = testing.DummyRequest()
        view = InstancesView(request)
        self.assertEqual(view.prefix, '/instances')
        self.assertEqual(view.initial_sort_key, '-launch_time')
