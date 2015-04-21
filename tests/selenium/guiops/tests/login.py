from selenium_api.selenium_api import Utilities
from guitester.guitester import GuiTester

class Test_login(Utilities):


    def setup(self):
        self.tester = GuiTester()

    def test_euca_login(self):
        self.tester.login()
        self.tester.logout()


if __name__ == "__main__":
   Test_login()



