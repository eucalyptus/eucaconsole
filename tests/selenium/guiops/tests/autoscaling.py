from guiops.guiops import GuiOps
from option_parser import Option_parser
import string, random, time
import logging, traceback


class ASG_operations_sequence(GuiOps):

    keypair = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDI1x6tEjkBQCCP0ssF69vAgP2xg+N9ScoTrqRqyl5w4qEgsV/AppfHHYRKYr0N/tTyG4/" \
                  "z1XGNrB2SaslnRpgEOsvMZldlOnqsUujL2fgoEg+/gB92+1JhZgTjU8nL5j5BFkVTh93nSHtXHdzYl7SjlXrv26ZbyuDwJmI+s6bJQk5noJ4Q4g" \
                  "7N/0y9pHRvezyhgxkyX7PQoA9WJm8SqlakyhMYa0j/baMhb/ehSI0VvwNodmcaWaS6Z2F4rZS4C2DmCUDXYy/1+0tiRTjHjlPbqRKCVKam8ImWy" \
                  "tlZD0zbdV/tpADxDpnhW2cPVpXcjy4sRzUCc8AZW+OE3LQxXild alicehubenko@Alices-MacBook-Pro.local"

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


    def asg_ops_test(self):

        self.tester.login(self.account, self.user, self.password)
        self.tester.create_launch_config_from_lc_lp("Alice-test-lc")
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = ASG_operations_sequence()
        ASG_operations_sequence.asg_ops_test(tester)
