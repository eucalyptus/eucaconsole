from guitester.guiec2 import GuiEC2
from guitester.guiiam import GuiIAM
import time


class Navigation_sequence(GuiEC2):


    def __init__(self):
        parser = Option_parser()
        self.console_url = parser.parse_options()['console_url']
        self.webdriver_url = parser.parse_options()['web_driver']
        self.account = parser.parse_options()['account']
        self.user = parser.parse_options()['user_name']
        self.password = parser.parse_options()['password']
        self.sauce = parser.parse_options()['sauce']
        self.browser = parser.parse_options()['browser']
        self.version = parser.parse_options()['version']
        self.platform = parser.parse_options()['platform']
        self.tester = GuiEC2(console_url=self.console_url, webdriver_url=self.webdriver_url, sauce=self.sauce, browser=self.browser, version=self.version, platform=self.platform)


    def navigation_test(self):

        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        self.tester.create_keypair_from_dashboard("keypair-test")
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Navigation_sequence()
        Navigation_sequence.navigation_test(tester)