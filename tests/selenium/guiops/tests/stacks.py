from guiops.guiops import GuiOps
from option_parser import Option_parser
import string, random, time


class Stack_operations_sequence(GuiOps):

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

    def stack_ops_test(self):
        self.tester.login(self.account, self.user, self.password)
        stack1_name = self.id_generator()+"-stack"
        self.tester.create_stack_from_dashboard(stack1_name)
        stack2_name = self.id_generator()+"-stack"
        self.tester.create_stack_from_lp(stack2_name)
        self.tester.delete_stack_from_lp(stack1_name)
        self.tester.delete_stack_from_detail_page(stack2_name)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Stack_operations_sequence()
        Stack_operations_sequence.stack_ops_test(tester)
