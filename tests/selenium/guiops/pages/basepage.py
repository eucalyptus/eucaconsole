from selenium_api.selenium_api import SeleniumApi
import time


class BasePage(SeleniumApi):

    _hp_logo_id = "hp-logo"
    _user_dropdown_css = 'section#user-dropdown-section>a>span'
    _user_help_link='//ul[@id="user-dropdown"]/li/a'
    _user_logout_id="logout"
    _region_selector_id = "selected-region"
    _region_dropdown_id = "region-dropdown"
    _dashboard_menuitem_id = "resource-menuitem-dashboard"
    _images_menuitem_id = "resource-menuitem-images"
    _images_menuitem_css = "#resource-menuitem-images"
    _images_parent_xpath = "//li/a[@id='resource-menuitem-images']"
    _instances_menuitem_id = "resource-menuitem-instances"
    _instance_types_menuitem_id = "resource-menuitem-instance_types"
    _stacks_menuitem_id = "resource-menuitem-stacks"
    _autoscaling_menuitem_id = "resource-menuitem-scalinggroups"
    _launchconfigs_menuitem_id = "resource-menuitem-launchconfigs"
    _volumes_meniuitem_id = "resource-menuitem-volumes"
    _snapshot_menuitem_id = "resource-menuitem-snapshots"
    _buckets_menuitem_id = "resource-menuitem-buckets"
    _sec_group_menuitem_id = "resource-menuitem-securitygroups"
    _keypair_menuitem_id = "resource-menuitem-keypairs"
    _elastic_ips_menuitem_id = "resource-menuitem-ipaddresses"
    _accounts_menuitem_id = "resource-menuitem-accounts"
    _users_menuitem_id = "resource-menuitem-users"
    _groups_menuitem_id = "resource-menuitem-groups"
    _roles_menuitem_id = "resource-menuitem-roles"
    _load_balancers_menuitem_id = "resource-menuitem-elb"
    _iam_accounts_menuitem_id = "resource-menuitem-accounts"
    _iam_users_menuitem_id = "resource-menuitem-users"
    _iam_groups_menuitem_id = "resource-menuitem-groups"
    _iam_roles_menuitem_id = "resource-menuitem-roles"
    _notification_id="notifications"
    _page_title_id = "pagetitle"
    _refresh_button_from_lp_id = "refresh-btn"
    _notification_css = '#notifications .message'

    def __init__(self, tester):
        self.tester = tester

    @classmethod
    def print_test_context(cls):
        print "\n##### Executing methods in {0}.{1} .....\n".format(cls.__module__, cls.__name__)

    def logout(self):
        self.tester.click_element_by_css(self._user_dropdown_css)
        self.tester.click_element_by_id(self._user_logout_id)

    def select_region(self, region):
        if self.tester.check_visibility_by_id(self._region_selector_id):
            self.tester.click_element_by_id(self._region_selector_id)
        self.tester.click_element_by_id(region)

    def get_region_list(self):
        """
        Gets regions list.
        """
        self.tester.click_element_by_id(self._region_selector_id)
        rlist = self.tester.store_text_by_id(self._region_dropdown_id)
        self.tester.click_element_by_id(self._region_selector_id)
        rlist = str(rlist)
        region_list = rlist.split()
        return region_list

    def goto_dashboard_via_menu(self):
        self.tester.scroll_to_element_by_id(self._dashboard_menuitem_id)
        self.tester.send_keys_by_id(self._dashboard_menuitem_id, "\n", clear_field=False)

    def goto_keypair_view_page_via_menu(self):
        self.tester.scroll_to_element_by_id(self._keypair_menuitem_id)
        self.tester.click_element_by_id_robust(self._keypair_menuitem_id, "create-keypair-btn")
        self.tester.scroll_to_element_by_id(self._dashboard_menuitem_id)

    def goto_images_view_via_menu(self):
        print "Scrolling to element by id {0}".format(self._images_menuitem_id)
        self.tester.scroll_to_element_by_id(self._images_menuitem_id)
        self.tester.click_element_by_id_text_by_id_robust(self._images_menuitem_id, self._page_title_id, "Images")
        self.tester.scroll_to_element_by_id(self._dashboard_menuitem_id)

    def goto_instances_via_menu(self):
        self.tester.scroll_to_element_by_id(self._instances_menuitem_id)
        self.tester.click_element_by_id_robust(self._instances_menuitem_id, "launch-instance-btn")
        self.tester.scroll_to_element_by_id(self._dashboard_menuitem_id)

    def goto_stacks_view_via_menu(self):
        self.tester.scroll_to_element_by_id(self._stacks_menuitem_id)
        self.tester.send_keys_by_id(self._stacks_menuitem_id, "\n", clear_field=False)

    def goto_elastic_ip_view_via_menu(self):
        self.tester.scroll_to_element_by_id(self._elastic_ips_menuitem_id)
        self.tester.send_keys_by_id(self._elastic_ips_menuitem_id, "\n", clear_field=False)

    def goto_security_groups_view_via_menu(self):
        self.tester.scroll_to_element_by_id(self._sec_group_menuitem_id)
        self.tester.click_element_by_id_robust(self._sec_group_menuitem_id, "create-securitygroup-btn")
        self.tester.scroll_to_element_by_id(self._dashboard_menuitem_id)

    def goto_load_balancers_view_via_menu(self):
        self.tester.scroll_to_element_by_id(self._load_balancers_menuitem_id)
        self.tester.send_keys_by_id(self._load_balancers_menuitem_id, "\n", clear_field=False)

    def goto_volumes_view_via_menu(self):
        self.tester.scroll_to_element_by_id(self._volumes_meniuitem_id)
        self.tester.send_keys_by_id(self._volumes_meniuitem_id, "\n", clear_field=False)

    def goto_snapshots_view_via_menu(self):
        self.tester.scroll_to_element_by_id(self._snapshot_menuitem_id)
        self.tester.send_keys_by_id(self._snapshot_menuitem_id, "\n", clear_field=False)

    def goto_buckets_view_via_menu(self):
        self.tester.scroll_to_element_by_id(self._buckets_menuitem_id)
        self.tester.send_keys_by_id(self._buckets_menuitem_id, "\n", clear_field=False)

    def goto_asg_lp_via_menu(self):
        self.tester.scroll_to_element_by_id(self._autoscaling_menuitem_id)
        self.tester.click_element_by_id_robust(self._autoscaling_menuitem_id, "create-scalinggroup-btn")
        self.tester.scroll_to_element_by_id(self._dashboard_menuitem_id)

    def goto_launch_config_view_via_menu(self):
        self.tester.scroll_to_element_by_id(self._launchconfigs_menuitem_id)
        self.tester.click_element_by_id_robust(self._launchconfigs_menuitem_id, "create-launchconfig-btn")
        self.tester.scroll_to_element_by_id(self._dashboard_menuitem_id)

    def goto_iam_users_view_via_menu(self):
        self.tester.scroll_to_element_by_id(self._iam_users_menuitem_id)
        self.tester.send_keys_by_id(self._iam_users_menuitem_id, "\n", clear_field=False)

    def goto_iam_groups_via_menu(self):
        self.tester.scroll_to_element_by_id(self._iam_groups_menuitem_id)
        self.tester.send_keys_by_id(self._iam_groups_menuitem_id, "\n", clear_field=False)

    def goto_iam_roles_via_menu(self):
        self.tester.scroll_to_element_by_id(self._iam_roles_menuitem_id)
        self.tester.send_keys_by_id(self._iam_roles_menuitem_id, "\n", clear_field=False)

    def get_notification(self):
        self.tester.wait_for_visible_by_id(BasePage._notification_id)
        notification = self.tester.store_text_by_id(BasePage._notification_id)
        print("Notification on page: " + notification)
