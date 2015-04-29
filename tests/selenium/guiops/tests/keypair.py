from guitester.guitester import GuiTester
from selenium_api.selenium_api import SeleniumApi


class Test_login(GuiTester):
    def __init__(self):
        self.tester = GuiTester("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def test_login(self):
        self.tester.login()
        self.tester.logout()

if __name__ == "__main__":
    tester = Test_login()
    Test_login.test_login(tester)
