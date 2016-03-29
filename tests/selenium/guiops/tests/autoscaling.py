import logging

from guiops.guiops import GuiOps
from option_parser import Option_parser


class AutoScalingOperationsSequence(GuiOps):
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
        self.tester = GuiOps(console_url=self.console_url, webdriver_url=self.webdriver_url, sauce=self.sauce,
                             browser=self.browser, version=self.version, platform=self.platform)
        logging.basicConfig(format='%(asctime)s %(message)s')

    def asg_ops_test(self):
        self.tester.login(self.account, self.user, self.password)
        launchconfig1_name = self.id_generator() + "-launch-config"
        scalinggroup1_name = self.id_generator() + "-auto-scaling-group"
        self.tester.create_launch_config_and_asg_from_lc_lp(lc_name=launchconfig1_name, asg_name=scalinggroup1_name,
                                                            max_capacity=2, desired_capacity=1, min_cpapacity=0)
        self.tester.delete_asg_from_lp(scalinggroup1_name)
        scalinggroup2_name = self.id_generator() + "-auto-scaling-group"
        self.tester.create_asg_from_asg_lp(launch_config_name=launchconfig1_name, asg_name=scalinggroup2_name)
        self.tester.delete_asg_from_lp(scalinggroup2_name)
        self.tester.delete_launch_config_from_lp(launchconfig1_name)
        launchconfig2_name = self.id_generator() + "-launch-config"
        self.tester.create_launch_config_from_lc_lp(launchconfig2_name)
        self.tester.create_asg_from_dashboard(launch_config_name=launchconfig2_name, asg_name=scalinggroup2_name,
                                              min_capacity=1, desired_capacity=1, max_capacity=1)
        self.tester.verify_scaling_history(scalinggroup2_name)
        self.tester.set_scaling_group_capacity(scalinggroup2_name, 0, 0, 1)
        self.tester.delete_asg_from_lp(scalinggroup2_name)
        self.tester.delete_launch_config_from_lp(launchconfig2_name)
        self.test_scaling_group_monitoring_page_with_monitoring_enabled()
        self.tester.logout()
        self.tester.exit_browser()

    def test_scaling_group_monitoring_page_with_monitoring_enabled(self):
        """Scaling group monitoring page should display charts when metrics collection is enabled and
           its launch config has monitoring enabled"""
        launchconfig3_name = self.id_generator() + "-launch-config"
        scalinggroup3_name = self.id_generator() + "-auto-scaling-group"
        self.tester.create_launch_config_and_asg_from_lc_lp(
                lc_name=launchconfig3_name, asg_name=scalinggroup3_name, enable_monitoring=True)
        self.tester.enable_metrics_collection_for_auto_scaling_group(scalinggroup3_name)
        self.tester.verify_charts_on_scaling_group_monitoring_page(scalinggroup3_name)
        self.tester.delete_asg_from_lp(scalinggroup3_name)
        self.tester.delete_launch_config_from_lp(launchconfig3_name)

if __name__ == '__main__':
    tester = AutoScalingOperationsSequence()
    AutoScalingOperationsSequence.asg_ops_test(tester)
