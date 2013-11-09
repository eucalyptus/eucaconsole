"""
Base classes for all tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
import unittest

from pyramid import testing

from koala.routes import urls


class BaseLiveTestCase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        for route in urls:
            self.config.add_route(route.name, route.pattern)

    def tearDown(self):
        testing.tearDown()


class BaseTestCase(unittest.TestCase):
    """Use this as a base when you need to run test with no routes automatically configured.
       Note: You probably want to use BaseLiveTestCase instead."""
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

