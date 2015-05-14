from guitester.guiec2 import GuiEC2
import time


class Security_group_operations_sequence(GuiEC2):


    def __init__(self):
        self.tester = GuiEC2("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def security_group_ops_test(self):

        self.tester.login("ui-test-acct-00", "admin", "mypassword0")

        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Security_group_operations_sequence()
        Security_group_operations_sequence.security_group_ops_test(tester)