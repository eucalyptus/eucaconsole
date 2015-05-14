from guitester.guitester import GuiTester
from guitester.guiec2 import GuiEC2
import time


class Keypair_operations_sequence(GuiEC2):

    keypair_name = "gui-test"

    keypair = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDI1x6tEjkBQCCP0ssF69vAgP2xg+N9ScoTrqRqyl5w4qEgsV/AppfHHYRKYr0N/tTyG4/" \
                  "z1XGNrB2SaslnRpgEOsvMZldlOnqsUujL2fgoEg+/gB92+1JhZgTjU8nL5j5BFkVTh93nSHtXHdzYl7SjlXrv26ZbyuDwJmI+s6bJQk5noJ4Q4g" \
                  "7N/0y9pHRvezyhgxkyX7PQoA9WJm8SqlakyhMYa0j/baMhb/ehSI0VvwNodmcaWaS6Z2F4rZS4C2DmCUDXYy/1+0tiRTjHjlPbqRKCVKam8ImWy" \
                  "tlZD0zbdV/tpADxDpnhW2cPVpXcjy4sRzUCc8AZW+OE3LQxXild alicehubenko@Alices-MacBook-Pro.local"

    def __init__(self):
        self.tester = GuiEC2("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def keypair_ops_test(self):

        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        self.tester.create_keypair_from_keypair_view_page(self.keypair_name)
        self.tester.delete_keypair_from_detail_page(self.keypair_name)
        self.tester.create_keypair_from_dashboard(self.keypair_name)
        self.tester.delete_keypair_from_view_page(self.keypair_name)
        self.tester.import_keypair(self.keypair, self.keypair_name)
        self.tester.delete_keypair_from_detail_page(self.keypair_name)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Keypair_operations_sequence()
        Keypair_operations_sequence.keypair_ops_test(tester)