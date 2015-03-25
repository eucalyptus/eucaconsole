from guiops.pages.loginpage import LoginPage, LoginTests
from guiops.pages.basepage import BasePage, LogoutTests
from guiops.pages.dashboard import Dashboard
from guiops.utilities import Utilities, Config
from guiops.guitester import GuiTestCase

class Test_login(Utilities):


   # def setup(self):
   #     self.tester = Utilities()

    def test_euca_login(self):
        LoginTests().test_euca_login()

        LogoutTests().test_euca_logout()


if __name__ == "__main__":
   Test_login()



