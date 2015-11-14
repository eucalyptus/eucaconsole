from pages.landingpage import LandingPage


class LaunchConfigLanding(LandingPage):
    def __init__(self, tester):
        self.tester = tester
        self.verify_lc_lp_loaded()

    _lc_landing_page_title = "Launch configurations"
    _create_lc_button_id = "create-launchconfig-btn"
    _lc_action_menu_id = "table-item-dropdown_{0}" #lc_name_required
    _view_details_actionmenu_item_css = "#item-dropdown_{0}>li>a"  #lc_name required
    _create_lc_like_this_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(2)>a"  #lc_name required
    _create_asg_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(3)>a"  #lc_name required
    _delete_lc_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(4)>a"  #lc_name required
    _lc_link_css = 'a[ng-href="/launchconfigs/{0}"]' #lc_name required
    _image_link_xpath = 'xpath=//a[@ng-href="/launchconfigs/{0}"]/../../td[2]/a' #lc_name required
    _key_xpath = 'xpath=//a[@ng-href="/scalinggroups/{0}"]/../../td[3]/a' #lc_name required
    _security_group_xpath = 'xpath=//a[@ng-href="/scalinggroups/{0}"]/../../td[4]/div/a' #lc_name required
    _search_input_field_css = ".search-input"

    def verify_lc_lp_loaded(self):
        self.tester.wait_for_text_present_by_id(LandingPage(self)._page_title_id, self._lc_landing_page_title)
        self.tester.wait_for_visible_by_id(LandingPage(self)._refresh_button_id)

    def click_action_create_lc_on_landing_page(self):
        self.tester.click_element_by_id(self._create_asg_button_id)

    def click_action_delete_asg_on_lp(self, asg_name):
        self.tester.click_element_by_id(self._asg_action_menu_id.format(asg_name))
        self.tester.click_element_by_css(self._delete_asg_actions_menu_item_css.format(asg_name))

    def click_action_manage_instances_on_lp(self, asg_name):
        self.tester.click_element_by_id(self._asg_action_menu_id.format(asg_name))
        self.tester.click_element_by_css(self._manage_instances_actions_menu_item_css.format(asg_name))

    def goto_asg_detail_page_via_actions_menu(self, asg_name):
        self.tester.click_element_by_id(self._asg_action_menu_id.format(asg_name))
        self.tester.click_element_by_css(self._view_details_actionmenu_item_css.format(asg_name))

    def click_action_manage_policies_on_lp(self, asg_name):
        self.tester.click_element_by_id(self._asg_action_menu_id.format(asg_name))
        self.tester.click_element_by_css(self._manage_policies_actions_menu_item_css.format(asg_name))

    def goto_asg_detail_page_via_link(self, asg_name):
        self.tester.click_element_by_css(self._asg_link_css.format(asg_name))

    def goto_launch_config_detail_page_via_link(self, asg_name):
        self.tester.click_element_by_xpath(self._launch_config_link_xpath.format(asg_name))

    def goto_instances_via_link(self, asg_name):
        self.tester.click_element_by_xpath(self._instances_xpath.format(asg_name))

    def get_availability_zones(self, asg_name):
        self.tester.store_text_by_xpath(self._availability_zones_xpath.format(asg_name))

    def get_asg_capacity(self, asg_name):
        self.tester.store_text_by_xpath(self._capacity_xpath.format(asg_name))

    def get_asg_status(self, asg_name):
        self.tester.store_text_by_xpath(self._status_xpath.format(asg_name))


