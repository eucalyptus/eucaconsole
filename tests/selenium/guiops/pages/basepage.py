from selenium_api.selenium_api import SeleniumApi
import time

class BasePage(SeleniumApi):

    _hamburger_css="#offcanvas-icon"
    _user_dropdown_css = 'section#user-dropdown-section>a>span'
    _user_help_link='//ul[@id="user-dropdown"]/li/a'
    _user_logout_id="logout"
    _dashboard_menuitem_id = "resource-menu-dashboard"
    _autoscaling_menuitem_id="resource-menuitem-scalinggroups"
    _launchconfigs_menuitem_id="resource-menuitem-launchconfigs"
    _storage_nav_bar_menu_id="resource-menu-storage"
    _volumes_meniuitem_id="resource-menuitem-volumes"
    _snapshot_menuitem_id="resource-menuitem-snapshots"
    _buckets_menuitem_id="esource-menuitem-buckets"
    _network_sec_nav_bar_menu_id="resource-menu-netsec"
    _sec_group_menuitem_id="resource-menuitem-securitygroups"
    _keypair_menuitem_id="resource-menuitem-keypairs"
    _ips_menuitem_id="resource-menuitem-eips"
    _users_menuitem_id="resource-menuitem-users"
    _groups_menuitem_id="resource-menuitem-groups"
    _roles_menuitem_id="resource-menuitem-roles"
    _notification_id="notifications"

    def __init__(self, tester):
        self.tester = tester

    def logout(self):
        self.tester.click_element_by_css(self._user_dropdown_css)
        self.tester.click_element_by_id(self._user_logout_id)

    def goto_dashboard_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._dashboard_menuitem_id)

    def goto_keypair_landing_via_menu(self):
        self.tester.click_element_by_css(self._hamburger_css)
        self.tester.click_element_by_id(self._keypair_menuitem_id)

    def get_notification(self):
        self.tester.wait_for_visible_by_id(BasePage._notification_id)
        notification = self.tester.store_text_by_id(BasePage._notification_id)
        print("Notification on page: " + notification)



