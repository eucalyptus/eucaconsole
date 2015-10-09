from guiops.guiops import GuiOps
from option_parser import Option_parser
import string, random, time


class Security_group_operations_sequence(GuiOps):

    s_group_description = "Security group created by security_group_sequence test"

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

    def security_group_ops_test(self):

        self.tester.login(self.account, self.user, self.password)
        s_group_name_1 = self.id_generator() + "_test_group"
        group1 = self.tester.create_security_group_from_dashboard(s_group_name_1, self.s_group_description)
        s_group_id_1 = group1.get("s_group_id")
        self.tester.add_tcp_22_rule_to_s_group(s_group_name_1, s_group_id_1)
        self.tester.add_custom_tcp_rule_to_s_group(s_group_name_1, s_group_id_1)
        self.tester.delete_security_group_from_detail_page(s_group_name_1, s_group_id_1)
        s_group_name_2 = self.id_generator() + "_test_group"
        group2 = self.tester.create_security_group_from_view_page(s_group_name_2, self.s_group_description)
        s_group_id_2 = group2.get("s_group_id")
        self.tester.add_ldap_rule_to_s_group(s_group_name_2, s_group_id_2)
        self.tester.delete_security_group_from_view_page(s_group_name_2, s_group_id_2)
        s_group_name_3 = self.id_generator() + "_test_group"
        group3 = self.tester.create_sesecurity_group_with_rules(s_group_name_3, self.s_group_description, "RDP", "Custom TCP", "22", "1024")
        s_group_id_3 = group3.get("s_group_id")
        self.tester.delete_security_group_from_detail_page(s_group_name_3, s_group_id_3)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Security_group_operations_sequence()
        Security_group_operations_sequence.security_group_ops_test(tester)
