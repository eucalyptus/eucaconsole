from pages.viewpage import ViewPage


class InstanceView(ViewPage):
    def __init__(self, tester):
        self.tester = tester
        self.verify_instance_view_page_loaded()

    _instances_view_page_title = "Instances"
    _launch_instance_button_id = "launch-instance-btn"
    _instance_action_menu_id = "table-item-dropdown_{0}"  #instance_id required
    _terminate_instance_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(13)>a"  #instance_id required
    _first_pending_instance_status_css = "status>span:contains('pending')"
    _first_instance_link_in_list_css = "#tableview>table>tbody>tr>td>a"
    _first_instance_status_css = "td:contains('{0}')~td>span"  #instance_id required; webdriver does not accept it
    _instance_link_css = 'a[ng-href="/instances/{0}"]'  #instance_id required;
    _view_details_actionmenu_item_css = "#item-dropdown_{0}>li>a"  #instance_id required
    _launch_more_like_this_actionmenu_item_css = "#item-dropdown_{0}>li:nth-of-type(3)>a"  #instance_id required
    _terminate_all_instances_btn_id = "terminate-instances-btn"
    _search_input_field_css = ".search-input"

    def verify_instance_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(ViewPage(self)._page_title_id, self._instances_view_page_title)
        self.tester.wait_for_visible_by_id(ViewPage(self)._refresh_button_id)

    def click_action_launch_instance_on_view_page(self):
        self.tester.click_element_by_id(self._launch_instance_button_id)

    def click_action_terminate_instance_on_view_page(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._terminate_instance_actions_menu_item_css.format(instance_id))

    def get_id_of_newly_launched_instance(self, name=None):
        contains_id = self.tester.get_attrubute_by_css(self._first_instance_link_in_list_css, "ng-href")
        instance_id = contains_id[-10:]
        print(instance_id)
        return instance_id

    def verify_instance_status_is_running(self, instance_id):
        NotImplementedError

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
        instance_name=None
        if len(full_name)>11:
            instance_name = full_name[:-13]
        return instance_name

    def click_terminate_all_instances_button(self):
        self.tester.click_element_by_id(self._terminate_all_instances_btn_id)

    def verify_there_are_no_running_instances(self):
        self.tester.send_keys_by_css(self._search_input_field_css, "running")
        self.tester.wait_for_text_present_by_css(ViewPage(self)._item_count_css,"0")






