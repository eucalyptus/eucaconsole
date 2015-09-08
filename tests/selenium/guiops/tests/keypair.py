from guiops.guiops import GuiOps
from option_parser import Option_parser
import string, random, time
import logging, traceback


class Keypair_operations_sequence(GuiOps):

    keypair = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDI1x6tEjkBQCCP0ssF69vAgP2xg+N9ScoTrqRqyl5w4qEgsV/AppfHHYRKYr0N/tTyG4/" \
                  "z1XGNrB2SaslnRpgEOsvMZldlOnqsUujL2fgoEg+/gB92+1JhZgTjU8nL5j5BFkVTh93nSHtXHdzYl7SjlXrv26ZbyuDwJmI+s6bJQk5noJ4Q4g" \
                  "7N/0y9pHRvezyhgxkyX7PQoA9WJm8SqlakyhMYa0j/baMhb/ehSI0VvwNodmcaWaS6Z2F4rZS4C2DmCUDXYy/1+0tiRTjHjlPbqRKCVKam8ImWy" \
                  "tlZD0zbdV/tpADxDpnhW2cPVpXcjy4sRzUCc8AZW+OE3LQxXild alicehubenko@Alices-MacBook-Pro.local"

    def id_generator(self, size = 6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for j in range(size))

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


    def keypair_ops_test(self):

        keypair1_name=self.id_generator()+"-key"
        self.tester.login(self.account, self.user, self.password)
        self.tester.create_keypair_from_keypair_view_page(keypair1_name)
        self.tester.delete_keypair_from_detail_page(keypair1_name)
        keypair2_name=self.id_generator()+"-key"
        self.tester.create_keypair_from_dashboard(keypair2_name)
        self.tester.delete_keypair_from_view_page(keypair2_name)
        keypair3_name=self.id_generator()+"-key"
        self.tester.import_keypair(self.keypair, keypair3_name)
        self.tester.delete_keypair_from_detail_page(keypair3_name)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Keypair_operations_sequence()
        Keypair_operations_sequence.keypair_ops_test(tester)