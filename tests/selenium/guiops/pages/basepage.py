from selenium_api.selenium_api import SeleniumApi
import time

class BasePage(SeleniumApi):

    _hamburger_css="#offcanvas-icon"
    _user_dropdown_css = 'section#user-dropdown-section>a>span'
    _user_help_link='//ul[@id="user-dropdown"]/li/a'
    _user_logout_id="logout"
    _dashboard_menuitem_id = "resource-menu-dashboard"
    _images_menuitem_id = "resource-menu-images"
    _instances_menuitem_id = "resource-menuitem-instances"
    _stacks_menuitem_id = ""
    _autoscaling_menuitem_id = "resource-menuitem-scalinggroups"
    _launchconfigs_menuitem_id =  "resource-menuitem-launchconfigs"
    _storage_nav_bar_menu_id = "resource-menu-storage"
    _volumes_meniuitem_id = "resource-menuitem-volumes"
    _snapshot_menuitem_id = "resource-menuitem-snapshots"
    _buckets_menuitem_id = "esource-menuitem-buckets"
    _network_sec_nav_bar_menu_id = "resource-menu-netsec"
    _sec_group_menuitem_id = "resource-menuitem-securitygroups"
    _keypair_menuitem_id = "resource-menuitem-keypairs"
    _elastic_ips_menuitem_id = "resource-menuitem-eips"
    _users_menuitem_id = "resource-menuitem-users"
    _groups_menuitem_id = "resource-menuitem-groups"
    _roles_menuitem_id = "resource-menuitem-roles"
    _load_balancers_menuitem_id = "resource-menuitem-elb"
    _iam_groups_menuitem_id = "resource-menuitem-users"
    _iam_users_menuitem_id = "resource-menuitem-groups"
    _iam_roles_menuitem_id = "resource-menuitem-roles"
    _notification_id="notifications"
    _page_title_id = "pagetitle"

    def __init__(self, tester):
        self.tester = tester

    def logout(self):
        self.tester.click_element_by_css(self._user_dropdown_css)
        self.tester.click_element_by_id(self._user_logout_id)

    def goto_dashboard_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._dashboard_menuitem_id)

    def goto_keypair_view_page_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._keypair_menuitem_id)

    def goto_images_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._images_menuitem_id)

    def goto_instances_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._instances_menuitem_id)

    def goto_stacks_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._stacks_menuitem_id)

    def goto_elestic_ip_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._elastic_ips_menuitem_id)

    def goto_security_groups_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._sec_group_menuitem_id)

    def goto_load_balancers_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._load_balancers_menuitem_id)

    def goto_volumes_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._volumes_meniuitem_id)

    def goto_snapshots_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._snapshot_menuitem_id)

    def goto_buckets_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._buckets_menuitem_id)

    def goto_asg_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._autoscaling_menuitem_id)

    def goto_launch_config_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._launchconfigs_menuitem_id)

    def goto_iam_users_view_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._iam_users_menuitem_id)

    def goto_iam_groups_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._iam_groups_menuitem_id)

    def goto_iam_roles_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._iam_roles_menuitem_id)

    def get_notification(self):
        self.tester.wait_for_visible_by_id(BasePage._notification_id)
        notification = self.tester.store_text_by_id(BasePage._notification_id)
        print("Notification on page: " + notification)



