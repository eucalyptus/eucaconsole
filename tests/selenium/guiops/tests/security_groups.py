from guitester.guiec2 import GuiEC2
import string, random, time


class Security_group_operations_sequence(GuiEC2):

    s_group_name = "test-123-sgroup"
    s_group_description = "Security group created by gui test"

    def __init__(self):
        self.tester = GuiEC2("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def id_generator(self, size = 6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for j in range(size))

    def security_group_ops_test(self):

        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        s_group_name = self.id_generator() + "_test_group"
        group1 = self.tester.create_security_group_from_dashboard(s_group_name, self.s_group_description)
        s_group_name_1 = group1.get("s_group_name")
        s_group_id_1 = group1.get("s_group_id")
        self.tester.add_tcp_22_rule_to_s_group(s_group_name_1, s_group_id_1)
        self.tester.add_custom_tcp_rule_to_s_group(s_group_name_1, s_group_id_1)
        self.tester.delete_security_group_from_detail_page(s_group_name_1, s_group_id_1)
        s_group_name = self.id_generator() + "_test_group"
        group2 = self.tester.create_security_group_from_view_page(s_group_name, self.s_group_description)
        s_group_name_2 = group2.get("s_group_name")
        s_group_id_2 = group2.get("s_group_id")
        self.tester.add_ldap_rule_to_s_group(s_group_name_2, s_group_id_2)
        self.tester.delete_security_group_from_view_page(s_group_name_2, s_group_id_2)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Security_group_operations_sequence()
        Security_group_operations_sequence.security_group_ops_test(tester)