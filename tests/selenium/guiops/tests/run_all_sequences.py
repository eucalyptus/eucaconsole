from guiops.guiops import GuiOps
from option_parser import Option_parser
from keypair import Keypair_operations_sequence
import string, random, time
import logging, traceback

class Complete_sequence(GuiOps):

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
        #logging.basicConfig(format='%(asctime)s %(message)s')


    def run_all_tests(self):

        Keypair_operations_sequence().keypair_ops_test()



if __name__ == '__main__':
        tester = Complete_sequence()
        Complete_sequence.run_all_tests(tester)







