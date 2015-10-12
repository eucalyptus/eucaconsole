from guiops.guiops import GuiOps
from pages.basepage import BasePage
from option_parser import Option_parser
import string, random, time
import logging, traceback


class Navigation_sequence(GuiOps):


    def id_generator(self, size = 6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

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
        self.tester = GuiOps(console_url=self.console_url, webdriver_url=self.webdriver_url, sauce=self.sauce, browser=self.browser, version=self.version, platform=self.platform)
        logging.basicConfig(format='%(asctime)s %(message)s')


    def navigation_test(self):

        self.tester.login(self.account, self.user, self.password)
        self.tester.goto_images_page_via_nav()
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Navigation_sequence()
        Navigation_sequence.navigation_test(tester)