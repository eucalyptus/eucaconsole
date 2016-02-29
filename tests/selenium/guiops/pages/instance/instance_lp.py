from pages.landingpage import LandingPage


class InstanceLanding(LandingPage):
    def __init__(self, tester):
        self.tester = tester
        self.print_test_context()
        self.verify_instance_view_page_loaded()

    _instances_view_page_title = "Instances"
    _launch_instance_button_id = "launch-instance-btn"
    _instance_action_menu_id = "table-item-dropdown_{0}"  # instance_id required
    _manage_volumes_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(7)>a"  # instance_id required
    _terminate_instance_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(13)>a"  # instance_id required
    _first_pending_instance_status_css = "status>span:contains('pending')"
    _first_instance_link_in_list_css = "#tableview>table>tbody>tr>td>a"
    _first_instance_status_css = "td:contains('{0}')~td>span"  # instance_id required; webdriver does not accept it
    _instance_link_css = 'a[ng-href="/instances/{0}"]'  # instance_id required;
    _view_details_actionmenu_item_css = "#item-dropdown_{0}>li>a"  # instance_id required
    _launch_more_like_this_actionmenu_item_css = "#item-dropdown_{0}>li:nth-of-type(3)>a"  # instance_id required
    _associate_ip_address_actionmenu_item_css = "#item-dropdown_{0}>li:nth-of-type(8)>a"  #instance_id required
    _disassociate_ip_address_actionmenu_item_css = "#item-dropdown_{0}>li:nth-of-type(9)>a"  #instance_id required
    _terminate_all_instances_btn_id = "terminate-instances-btn"
    _more_actions_menu_terminate_instances_css = "#more-actions-dropdown .more-actions-terminate"
    _search_input_field_css = ".search-input"
    _elastic_ip_link_css = 'a[href="/ipaddresses/{0}"]'

    def verify_instance_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(LandingPage(self)._page_title_id, self._instances_view_page_title)
        self.tester.wait_for_visible_by_id(LandingPage(self)._refresh_button_id)

    def click_action_launch_instance_on_landing_page(self):
        self.tester.click_element_by_id(self._launch_instance_button_id)

    def click_action_associate_ip_address_from_landing_page(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._associate_ip_address_actionmenu_item_css.format(instance_id))

    def click_action_disassociate_ip_address_from_landing_page(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._disassociate_ip_address_actionmenu_item_css.format(instance_id))

    def click_action_terminate_instance_on_view_page(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._terminate_instance_actions_menu_item_css.format(instance_id))

    def click_action_manage_volumes_on_view_page(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._manage_volumes_actions_menu_item_css.format(instance_id))

    def get_id_of_newly_launched_instance(self, name=None):
        contains_id = self.tester.get_attribute_by_css(self._first_instance_link_in_list_css, "ng-href")
        instance_id = contains_id[-10:]
        print(instance_id)
        return instance_id

    def verify_instance_status_is_running(self, instance_id):
        raise NotImplementedError


    def goto_instance_detail_page_via_link(self, instance_id):
        self.tester.click_element_by_css(self._instance_link_css.format(instance_id))

    def goto_instance_detail_page_via_actions(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._view_details_actionmenu_item_css.format(instance_id))

    def click_action_launch_more_like_this(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._launch_more_like_this_actionmenu_item_css.format(instance_id))

    def get_instance_name(self, instance_id):
        full_name = self.tester.store_text_by_css(self._instance_link_css.format(instance_id))
        instance_name = None
        if len(full_name) > 11:
            instance_name = full_name[:-13]
        return instance_name

    def click_terminate_all_instances_button(self):
        self.tester.click_element_by_id(LandingPage._select_all_items_tableview_checkbox_id)
        self.tester.click_element_by_id(LandingPage._more_actions_button_id)
        self.tester.click_element_by_css(self._more_actions_menu_terminate_instances_css)

    def verify_there_are_no_running_instances(self):
        self.tester.send_keys_by_css(self._search_input_field_css, "running")
        self.tester.wait_for_text_present_by_css(LandingPage(self)._item_count_css, "0")

    def verify_elastic_ip_address_on_instance_lp(self, elastic_ip):
        self.tester.wait_for_element_present_by_link_text(elastic_ip)
        self.tester.wait_for_text_present_by_css(self._elastic_ip_link_css.format(elastic_ip), elastic_ip)

    def verify_elastic_ip_address_off_instance_lp(self, elastic_ip):
        self.tester.wait_for_element_not_present_by_css(self._elastic_ip_link_css.format(elastic_ip))






