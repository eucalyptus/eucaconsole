from guiops.guiops import GuiOps
from option_parser import Option_parser
import string, random, time
import logging, traceback


class ASG_operations_sequence(GuiOps):


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
        LaunchConfig1_name = self.id_generator()+"-launch-config"
        ASG1_name = self.id_generator()+"-auto-scaling-group"
        self.tester.create_launch_config_and_asg_from_lc_lp(lc_name=LaunchConfig1_name, asg_name=ASG1_name)
        self.tester.delete_asg_from_lp(ASG1_name)
        ASG2_name = self.id_generator()+"-auto-scaling-group"
        self.tester.create_asg_from_asg_lp(launch_config_name=LaunchConfig1_name, asg_name=ASG2_name)
        self.tester.delete_asg_from_lp(ASG2_name)
        self.tester.delete_launch_config_from_lp(LaunchConfig1_name)
        LaunchConfig2_name = self.id_generator()+"-launch-config"
        self.tester.create_launch_config_from_lc_lp(LaunchConfig2_name)
        self.tester.create_asg_from_dashboard(launch_config_name=LaunchConfig2_name, asg_name=ASG2_name, min_capacity=1, desired_capacity=1, max_capacity=1)
        self.tester.verify_scaling_history(ASG2_name)
        self.tester.set_scaling_group_capacity(ASG2_name, 0, 0, 1)
        self.tester.delete_asg_from_lp(ASG2_name)
        self.tester.delete_launch_config_from_lp(LaunchConfig2_name)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = ASG_operations_sequence()
        ASG_operations_sequence.asg_ops_test(tester)
