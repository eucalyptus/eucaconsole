from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.autoscaling.launch_config_lp import LaunchConfigLanding
from pages.autoscaling.create_launch_config import CreateLaunchConfigPage

class GuiASG(GuiTester):

    def __init__(self, console_url, sauce=False, webdriver_url=None, browser=None, version=None, platform=None):
        super(GuiASG, self).__init__(console_url, webdriver_url=webdriver_url, sauce=sauce, browser=browser, version=version, platform=platform)

    def create_launch_config_from_lc_lp(self, lc_name):
        BasePage(self).goto_launch_config_view_via_menu()
        LaunchConfigLanding(self).click_create_lc_button_on_landing_page()
        CreateLaunchConfigPage(self).create_new_launch_config(lc_name)

    def create_launch_config_and_asg_from_lc_lp(self, lc_name, asg_name):
        BasePage(self).goto_launch_config_view_via_menu()
        LaunchConfigLanding(self).click_create_lc_button_on_landing_page()
        CreateLaunchConfigPage(self).create_new_launch_config_and_asg(lc_name, asg_name)
