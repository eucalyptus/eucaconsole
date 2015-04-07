
from guiops.pages.dashboard import Dashboard
from guiops.utilities import Utilities
from guiops.guitester.guitester import GuiTester

class Test_login(Utilities):


    def setup(self):
        self.tester = GuiTester()

    def test_euca_login(self):
        self.tester.login()
        self.tester.logout()


if __name__ == "__main__":
   Test_login()



