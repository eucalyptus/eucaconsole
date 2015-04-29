from selenium_api.selenium_api import SeleniumApi
from guitester.guitester import GuiTester


class Navigation_sequence(GuiTester):

    def __init__(self):
        self.tester = GuiTester("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def navigation_test(self):

        self.tester.login()

        self.tester.logout()

if __name__ == '__main__':
        tester = Navigation_sequence()
        Navigation_sequence.navigation_test(tester)