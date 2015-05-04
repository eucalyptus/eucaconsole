from selenium_api.selenium_api import SeleniumApi
from guitester.guitester import GuiTester


class Navigation_sequence(GuiTester):

    def __init__(self):
        self.tester = GuiTester("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def navigation_test(self):

        #self.tester.wait_for_element_present_by_id("euca")
        #self.tester.wait_for_visible_by_id("euca")

        self.tester.click_element_by_id("euca")

        #self.tester.login()

        #self.tester.wait_for_element_not_present_by_id("boo")

        #self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Navigation_sequence()
        Navigation_sequence.navigation_test(tester)