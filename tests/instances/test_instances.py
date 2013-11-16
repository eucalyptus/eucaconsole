"""
Instances tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing

from tests import BaseViewTestCase


class InstancesViewTests(BaseViewTestCase):

    def test_instances_view_defaults(self):
        from koala.views.instances import InstancesView
        request = testing.DummyRequest()
        view = InstancesView(request)
        self.assertEqual(view.prefix, '/instances')
        self.assertEqual(view.initial_sort_key, '-launch_time')
