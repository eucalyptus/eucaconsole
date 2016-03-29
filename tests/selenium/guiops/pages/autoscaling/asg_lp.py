from pages.landingpage import LandingPage


class ASGLanding(LandingPage):
    def __init__(self, tester):
        self.tester = tester
        self.print_test_context()
        self.verify_asg_lp_loaded()

    _asg_landing_page_title = "Scaling groups"
    _asg_link_css = 'a[ng-href="/scalinggroups/{0}"]'  # asg_name_required
    _create_asg_button_id = "create-scalinggroup-btn"
    _asg_action_menu_id = "table-item-dropdown_{0}"  # asg_name_required
    _asg_item_row_prefix_css = '#tableview tr[data-item-id="{0}"]'  # asg_name required
    _asg_item_row_actions_css_prefix = '{0} td:last-child .actions'.format(_asg_item_row_prefix_css)
    _asg_action_menu_css = '{0} .dropdown'.format(_asg_item_row_actions_css_prefix)
    _view_details_actionmenu_item_css = '{0} a.action-view-details'.format(_asg_item_row_actions_css_prefix)
    _manage_instances_actions_menu_item_css = '{0} a.action-manage-instances'.format(_asg_item_row_actions_css_prefix)
    _manage_policies_actions_menu_item_css = '{0} a.action-manage-policies'.format(_asg_item_row_actions_css_prefix)
    _delete_asg_actions_menu_item_css = '{0} a.action-delete'.format(_asg_item_row_actions_css_prefix)
    _launch_config_link_css = '{0} td.launchconfigs a'.format(_asg_item_row_prefix_css)
    _instances_css = '{0} td.instances a'.format(_asg_item_row_prefix_css)
    _instances_xpath = 'xpath=//a[@ng-href="/scalinggroups/{0}"]/../../td[3]/a'  # asg_name required
    _availability_zones_xpath = 'xpath=//a[@ng-href="/scalinggroups/{0}"]/../../td[4]'  # asg_name required
    _capacity_xpath = 'xpath=//a[@ng-href="/scalinggroups/{0}"]/../../td[5]'  # asg_name required
    _status_xpath = 'xpath=//a[@ng-href="/scalinggroups/{0}"]/../../td[6]'  # asg_name required
    _search_input_field_css = ".search-input"

    def verify_asg_lp_loaded(self):
        self.tester.wait_for_text_present_by_id(LandingPage(self)._page_title_id, self._asg_landing_page_title)
        self.tester.wait_for_visible_by_id(LandingPage(self)._refresh_button_id)

    def click_action_create_asg_on_landing_page(self):
        self.tester.click_element_by_id(self._create_asg_button_id)

    def click_action_delete_asg_on_lp(self, asg_name):
        self.tester.click_element_by_css(self._asg_action_menu_css.format(asg_name))
        self.tester.click_element_by_css_robust(
            self._delete_asg_actions_menu_item_css.format(asg_name), "#delete_scalinggroup_submit_button")

    def click_action_manage_instances_on_lp(self, asg_name):
        self.tester.click_element_by_css(self._asg_action_menu_css.format(asg_name))
        self.tester.click_element_by_css(self._manage_instances_actions_menu_item_css.format(asg_name))

    def goto_asg_detail_page_via_actions_menu(self, asg_name):
        self.tester.click_element_by_css(self._asg_action_menu_css.format(asg_name))
        self.tester.click_element_by_css(self._view_details_actionmenu_item_css.format(asg_name))

    def click_action_manage_policies_on_lp(self, asg_name):
        self.tester.click_element_by_css(self._asg_action_menu_css.format(asg_name))
        self.tester.click_element_by_css(self._manage_policies_actions_menu_item_css.format(asg_name))

    def goto_asg_detail_page_via_link(self, asg_name):
        self.tester.click_element_by_css(self._asg_link_css.format(asg_name))

    def goto_launch_config_detail_page_via_link(self, asg_name):
        self.tester.click_element_by_css(self._launch_config_link_css.format(asg_name))

    def goto_instances_via_link(self, asg_name):
        self.tester.click_element_by_css(self._instances_css.format(asg_name))

    def get_availability_zones(self, asg_name):
        self.tester.store_text_by_xpath(self._availability_zones_xpath.format(asg_name))

    def get_asg_capacity(self, asg_name):
        self.tester.store_text_by_xpath(self._capacity_xpath.format(asg_name))

    def get_asg_status(self, asg_name):
        self.tester.store_text_by_xpath(self._status_xpath.format(asg_name))

    def verify_asg_present(self, asg_name):
        self.tester.wait_for_element_present_by_css(self._asg_link_css.format(asg_name))
