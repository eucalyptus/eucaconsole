from guiops.utilities import Utilities



class BasePage(Utilities):


    _euca_logo_id="logo"
    _euca_logo_bar_id="logobar"
    _user_dropdown_xpath= '//section[@id="user-dropdown-section"]/a/span'
    _user_help_link='//ul[@id="user-dropdown"]/li/a'
    _user_logout_id="logout"
    _dashboard_nav_bar_button_id="resource-menu-dashboard"
    _images_nav_bar_menu_id="resource-menu-images"
    _instances_nav_bar_menu_id="resource-menu-instances"
    _autoscaling_nav_bar_menu_id="resource-menu-autoscaling"
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
    _iam_nav_bar_menu_id="resource-menu-iam"
    _users_menuitem_id="resource-menuitem-users"
    _groups_menuitem_id="resource-menuitem-groups"
    _roles_menuitem_id="resource-menuitem-roles"
    _hamburger_menu_xpath='//nav[@ id="logobar"]/a/'
    _notification_id="notifications"



    def assert_euca_logo(self):
        self.tester.wait_for_visible("ID",self._euca_logo_id)

    def assert_euca_logobar(self):
        self.tester.wait_for_visible("ID",self._euca_logo_bar_id)

    def __init__(self, tester):
        self.tester = tester
        self.assert_euca_logo()
        self.assert_euca_logobar()

    def logout(self):
        self.tester.click_on_visible("XPATH",BasePage._user_dropdown_xpath)
        self.tester.click_on_visible("ID", BasePage._user_logout_id)

    def from_dashboard_goto_keypairs_lp_via_nav_bar(self):
            self.tester.click_on_visible("ID",BasePage._network_sec_nav_bar_menu_id)
            self.tester.click_on_visible("ID",BasePage._keypair_menuitem_id)

    def click_nav_bar_dashboard_link(self):
            self.tester.click_on_visible("XPATH",BasePage._dashboard_nav_bar_button_id)


