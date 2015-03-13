import unittest

from guiops.tests.base import BaseTestCase
from guiops.tests.login import LoginTest

class Navigation_sequence_run(BaseTestCase):
     def navigation_sequence(self):
        LoginTest.test_euca_login()
        LoginTest.test_euca_logout()

if __name__ == '__main__':
        unittest.main()