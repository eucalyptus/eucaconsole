from guitester.guitester import GuiTester
import time


class Keypair_operations(GuiTester):

    def __init__(self):
        self.tester = GuiTester("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def keypair_sequence(self):

        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        self.tester.create_keypair_from_dashboard("keypair1")
        self.delete_keypair_from_detail_page("keypair1")
        self.tester.exit_browser()



if __name__ == '__main__':
        tester = Keypair_operations()
        Keypair_operations.keypair_sequence(tester)