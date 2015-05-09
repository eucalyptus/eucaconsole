from guitester.guitester import GuiTester
import time


class Navigation_sequence(GuiTester):

    def __init__(self):
        self.tester = GuiTester("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def navigation_test(self):

        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        self.tester.goto_dashboard()
        #self.tester.click_element_by_css("#zone-selector>a")
        #self.tester.click_element_by_css("ul#zone-dropdown>li:nth-of-type(2)>a")
        time.sleep(5)
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Navigation_sequence()
        Navigation_sequence.navigation_test(tester)