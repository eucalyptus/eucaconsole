from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.autoscaling.launch_config_lp import LaunchConfigLanding
from pages.autoscaling.create_launch_config import CreateLaunchConfigPage

class GuiASG(GuiTester):

    def __init__(self, console_url, sauce=False, webdriver_url=None, browser=None, version=None, platform=None):
        super(GuiASG, self).__init__(console_url, webdriver_url=webdriver_url, sauce=sauce, browser=browser, version=version, platform=platform)

    def create_launch_config_from_lc_lp(self, lc_name,instance_type=None, image="centos", key_name="None (advanced option)",
                               security_group="default", user_data_text=None, user_data_file_path=None, role=None, create_asg=False, kernel_id=None, ramdisk_id=None,
                               enable_monitoring=True):
        BasePage(self).goto_launch_config_view_via_menu()
        LaunchConfigLanding(self).click_create_lc_button_on_landing_page()
        CreateLaunchConfigPage(self).create_new_launch_config(lc_name, instance_type, image, key_name,
                               security_group, user_data_text, user_data_file_path, role, create_asg, kernel_id, ramdisk_id, enable_monitoring)

    def create_launch_config_and_asg_from_lc_lp(self, lc_name, asg_name):
        BasePage(self).goto_launch_config_view_via_menu()
        LaunchConfigLanding(self).click_create_lc_button_on_landing_page()
        CreateLaunchConfigPage(self).create_new_launch_config_and_asg(lc_name, asg_name)

    def create_asg_from_dashboard(self, asg_name):
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self)
