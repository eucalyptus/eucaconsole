from guitester.guitester import GuiTester
from guitester.guiec2 import GuiEC2
import time


class Navigation_sequence(GuiTester, GuiEC2):

    keypair_name = "gui-test"

    def __init__(self):
        self.tester = GuiTester("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def navigation_test(self):

        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        self.tester.create_keypair_from_keypair_landing(self.keypair_name)
        self.tester.delete_keypair_from_detail_page(self.keypair_name)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Navigation_sequence()
        Navigation_sequence.navigation_test(tester)