import unittest
from guiops.pages.basepage import LogoutTests
from guiops.utilities import Utilities
from guiops.pages.loginpage import LoginTests

class Navigation_sequence(Utilities):
     def navigation_sequence(self):
        LoginTests.test_euca_login()
        LogoutTests.test_euca_logout()

if __name__ == '__main__':
        unittest.main()