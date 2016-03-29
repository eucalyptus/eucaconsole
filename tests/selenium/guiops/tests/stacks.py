from guiops.guiops import GuiOps
from option_parser import Option_parser


class Stack_operations_sequence(GuiOps):
    TEMPLATE_URL = 'https://raw.githubusercontent.com/eucalyptus/eucaconsole/19b2a55ce33e0d76567bff9541319bb7b51e18d4/eucaconsole/cf-templates/Euca%20Stacks/Basic%20Instance.json'

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
        keypair_name = self.id_generator()+"-keypair"
        self.tester.create_keypair_from_dashboard(keypair_name)

        # test stack from sample
        stack1_name = "test-" + self.id_generator() + "-stack"
        self.tester.create_stack_from_dashboard(stack1_name)
        stack2_name = "test-" + self.id_generator() + "-stack"
        self.tester.create_stack_from_lp(stack2_name)
        # update a stack
        self.tester.update_stack_from_lp(stack2_name)
        # delete the stacks
        self.tester.delete_stack_from_lp(stack1_name)
        self.tester.delete_stack_from_detail_page(stack2_name)

        #test stack from uploaded template
        stack3_name = "test-" + self.id_generator() + "-stack"
        self.tester.create_stack_from_dashboard(stack3_name, template_url=self.TEMPLATE_URL)
        self.tester.delete_stack_from_lp(stack3_name)

        self.tester.delete_keypair_from_detail_page(keypair_name)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Stack_operations_sequence()
        Stack_operations_sequence.stack_ops_test(tester)
