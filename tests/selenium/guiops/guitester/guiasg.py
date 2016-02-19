from dialogs.asg_dialogs import DeleteASGModal
from dialogs.launch_config_dialogs import DeleteLaunchConfigModal
from guitester import GuiTester
from pages.autoscaling.asg_detail import ASGDetailPage
from pages.autoscaling.asg_lp import ASGLanding
from pages.autoscaling.create_asg import CreateASGPage
from pages.autoscaling.create_launch_config import CreateLaunchConfigPage
from pages.autoscaling.launch_config_lp import LaunchConfigLanding
from pages.basepage import BasePage
from pages.dashboard import Dashboard


class GuiASG(GuiTester):
    def __init__(self, console_url, sauce=False, webdriver_url=None, browser=None, version=None, platform=None):
        super(GuiASG, self).__init__(console_url, webdriver_url=webdriver_url, sauce=sauce, browser=browser,
                                     version=version, platform=platform)

    def create_launch_config_from_lc_lp(self, lc_name, instance_type=None, image="centos",
                                        key_name="None (advanced option)",
                                        security_group="default", user_data_text=None, user_data_file_path=None,
                                        role=None, create_asg=False, kernel_id=None, ramdisk_id=None,
                                        enable_monitoring=True):
        BasePage(self).goto_launch_config_view_via_menu()
        LaunchConfigLanding(self).click_create_lc_button_on_landing_page()
        CreateLaunchConfigPage(self).create_new_launch_config(lc_name, instance_type, image, key_name,
                                                              security_group, user_data_text, user_data_file_path, role,
                                                              create_asg, kernel_id, ramdisk_id, enable_monitoring)
        BasePage(self).goto_launch_config_view_via_menu()
        LaunchConfigLanding(self).verify_launch_config_is_present(lc_name)

    def create_launch_config_and_asg_from_lc_lp(self, lc_name, asg_name, instance_type=None, image="centos",
                                         key_name="None (advanced option)",
                                         security_group="default", user_data_text=None, user_data_file_path=None,
                                         role=None, create_asg=True, kernel_id=None, ramdisk_id=None,
                                         enable_monitoring=True, availabilityzones=None, min_cpapacity=None,
                                         desired_capacity=None, max_capacity=None, grace_period=None,
                                         loadbalancers=None):
        BasePage(self).goto_launch_config_view_via_menu()
        LaunchConfigLanding(self).click_create_lc_button_on_landing_page()
        CreateLaunchConfigPage(self).create_new_launch_config_and_asg(lc_name, asg_name,instance_type=instance_type, image=image,
                                         key_name=key_name,
                                         security_group=security_group, user_data_text=user_data_text, user_data_file_path=user_data_file_path,
                                         role=role, create_asg=create_asg, kernel_id=kernel_id, ramdisk_id=ramdisk_id,
                                         enable_monitoring=enable_monitoring, availabilityzones=availabilityzones, min_cpapacity=min_cpapacity,
                                         desired_capacity=desired_capacity, max_capacity=max_capacity, grace_period=grace_period,
                                         loadbalancers=loadbalancers)
        BasePage(self).goto_asg_lp_via_menu()
        ASGLanding(self).verify_asg_present(asg_name)
        BasePage(self).goto_launch_config_view_via_menu()
        LaunchConfigLanding(self).verify_launch_config_is_present(lc_name)

    def create_asg_from_dashboard(self, asg_name, launch_config_name, availabilityzones=None, min_capacity=None,
                                  desired_capacity=None, max_capacity=None, grace_period=None, loadbalancers=None):
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_asg_link_from_dashboard()
        CreateASGPage(self).create_asg(asg_name, launch_config_name, availabilityzones, min_capacity, desired_capacity,
                                       max_capacity, grace_period, loadbalancers)
        ASGDetailPage(self).confirm_scaling_policy_modal()
        BasePage(self).goto_asg_lp_via_menu()
        ASGLanding(self).verify_asg_present(asg_name)

    def create_asg_from_asg_lp(self, asg_name, launch_config_name, availabilityzones=None, min_capacity=None,
                               desired_capacity=None, max_capacity=None, grace_period=None, loadbalancers=None):
        BasePage(self).goto_asg_lp_via_menu()
        ASGLanding(self).click_action_create_asg_on_landing_page()
        CreateASGPage(self).create_asg(asg_name, launch_config_name, availabilityzones, min_capacity, desired_capacity,
                                       max_capacity, grace_period, loadbalancers)
        ASGDetailPage(self).confirm_scaling_policy_modal()
        BasePage(self).goto_asg_lp_via_menu()
        ASGLanding(self).verify_asg_present(asg_name)

    def delete_asg_from_lp(self, asg_name):
        BasePage(self).goto_asg_lp_via_menu()
        ASGLanding(self).click_action_delete_asg_on_lp(asg_name)
        DeleteASGModal(self).delete_asg()

    def delete_launch_config_from_lp(self, lc_name):
        BasePage(self).goto_launch_config_view_via_menu()
        LaunchConfigLanding(self).click_action_delete_lc_on_lp(lc_name)
        DeleteLaunchConfigModal(self).delete_launch_config()

    def verify_scaling_history(self, asg_name):
        """
        Must have scaling group created and should have some history, like if you create
        with min/desired/max = 1
        """
        BasePage(self).goto_asg_lp_via_menu()
        ASGLanding(self).goto_asg_detail_page_via_link(asg_name)
        ASGDetailPage(self).verify_scaling_history(asg_name)

    def set_scaling_group_capacity(self, asg_name, min_capacity=None, desired_capacity=None, max_capacity=None):
        BasePage(self).goto_asg_lp_via_menu()
        ASGLanding(self).goto_asg_detail_page_via_link(asg_name)
        ASGDetailPage(self).goto_general_tab(asg_name)
        ASGDetailPage(self).change_capacity_on_detail_page(min_capacity, desired_capacity, max_capacity)
        ASGDetailPage(self).verify_capacity_entries(min_capacity, desired_capacity, max_capacity)

    def enable_metrics_collection_for_auto_scaling_group(self, asg_name):
        BasePage(self).goto_asg_lp_via_menu()
        ASGLanding(self).goto_asg_detail_page_via_actions_menu(asg_name)
        ASGDetailPage(self).goto_monitoring_tab(asg_name)
        ASGDetailPage(self).enable_metrics_collection(asg_name)

    def verify_charts_on_scaling_group_monitoring_page(self, asg_name):
        """
        Scaling Group Monitoring page should display charts when scaling group has metrics collection enabled
        and launch configuration has monitoring enabled
        :param asg_name:
        """
        BasePage(self).goto_asg_lp_via_menu()
        ASGLanding(self).goto_asg_detail_page_via_actions_menu(asg_name)
        ASGDetailPage(self).goto_monitoring_tab(asg_name)
        ASGDetailPage(self).verify_charts_on_monitoring_page(asg_name)
