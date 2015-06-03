from pages.viewpage import ViewPage


class InstanceView(ViewPage):
    def __init__(self, tester):
        self.tester = tester
        self.verify_instance_view_page_loaded()

    _instances_view_page_title = "Instances"
    _instance_action_menu_id = "table-item-dropdown_{0}"  #instance_id required
    _terminate_instance_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(13)>a"  #instance_id required
    _first_pending_instance_status_css = "status>span:contains('pending')"
    _first_instance_link_in_list_css = "#tableview>table>tbody>tr>td>a"
    _first_instance_status_css = "td:contains('{0}')~td>span"  #instance_id required; webdriver does not accept it
    _instance_link_css = 'a[ng-href="/instances/{0}"]'#instance_id required;

    def verify_instance_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(ViewPage(self)._page_title_id, self._instances_view_page_title)
        self.tester.wait_for_visible_by_id(ViewPage(self)._refresh_button_id)

    def click_action_terminate_instance_on_view_page(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._terminate_instance_actions_menu_item_css.format(instance_id))

    def get_id_of_newly_launched_instance(self, name=None):
        contains_id = self.tester.get_attrubute_by_css(self._first_instance_link_in_list_css, "ng-href")
        instance_id = contains_id[-10:]
        print(instance_id)
        return instance_id

    def wait_for_instance_status_go_to_running(self, instance_id):
        NotImplementedError


    def goto_instance_detail_page_via_link(self, instance_id):
        self.tester.click_element_by_css(self._instance_link_css.format(instance_id))

