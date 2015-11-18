from pages.landingpage import LandingPage


class LaunchConfigLanding(LandingPage):
    def __init__(self, tester):
        self.tester = tester
        self.verify_lc_lp_loaded()

    _lc_landing_page_title = "Launch configurations"
    _create_lc_button_id = "create-launchconfig-btn"
    _lc_action_menu_id = "table-item-dropdown_{0}" #lc_name_required
    _lc_link_css = 'a[href="/launchconfigs/{0}"]' #lc_name_required
    _delete_lc_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(4)>a"  #lc_name required
    _create_lc_like_this_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(2)>a"  #lc_name required
    _view_details_actionmenu_item_css = "#item-dropdown_{0}>li>a"  #lc_name required
    _create_asg_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(3)>a"  #lc_name required
    _image_link_xpath ='xpath=//a[@ng-href="/launchconfigs/{0}"]/../../td[2]/a' #lc_name required
    _search_input_field_css = ".search-input"

    def verify_lc_lp_loaded(self):
        self.tester.wait_for_text_present_by_id(LandingPage(self)._page_title_id, self._lc_landing_page_title)
        self.tester.wait_for_visible_by_id(LandingPage(self)._refresh_button_id)

    def click_create_lc_button_on_landing_page(self):
        self.tester.click_element_by_id(self._create_lc_button_id)

    def click_action_delete_lc_on_lp(self, lc_name):
        self.tester.click_element_by_id(self._lc_action_menu_id.format(lc_name))
        self.tester.click_element_by_css(self._delete_lc_actions_menu_item_css.format(lc_name))

    def click_action_create_lc_like_this_on_lp(self, lc_name):
        self.tester.click_element_by_id(self._lc_action_menu_id.format(lc_name))
        self.tester.click_element_by_css(self._create_lc_like_this_actions_menu_item_css.format(lc_name))

    def goto_lc_detail_page_via_actions_menu(self, lc_name):
        self.tester.click_element_by_id(self._lc_action_menu_id.format(lc_name))
        self.tester.click_element_by_css(self._view_details_actionmenu_item_css.format(lc_name))

    def click_action_create_asg_on_lp(self, lc_name):
        self.tester.click_element_by_id(self._lc_action_menu_id.format(lc_name))
        self.tester.click_element_by_css(self._create_asg_actions_menu_item_css.format(lc_name))

    def goto_lc_detail_page_via_link(self, lc_name):
        self.tester.click_element_by_css(self._lc_link_css.format(lc_name))

    def goto_image_detail_page_via_link(self, lc_name):
        self.tester.click_element_by_xpath(self._image_link_xpath.format(lc_name))

    def verify_launch_config_is_present(self, lc_name):
        self.tester.wait_for_element_present_by_css(self._lc_link_css.format(lc_name))



