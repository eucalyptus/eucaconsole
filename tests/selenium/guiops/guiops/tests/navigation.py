import unittest
import guiops.pages
from guiops.utilities import Utilities


class Navigation_sequence(Utilities):
     def navigation_sequence(self):
        guiops.pages.loginpage.login()
        guiops.pages.basepage.logout()

if __name__ == '__main__':
        unittest.main()