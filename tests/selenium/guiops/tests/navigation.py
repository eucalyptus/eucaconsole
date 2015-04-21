import unittest
import pages
from selenium_api.selenium_api import Utilities


class Navigation_sequence(Utilities):
     def navigation_sequence(self):
        pages.loginpage.login()
        pages.basepage.logout()

if __name__ == '__main__':
        unittest.main()