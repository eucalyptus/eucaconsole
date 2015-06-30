from pages.viewpage import ViewPage


class SnapshotView(ViewPage):
    def __init__(self, tester):
        self.tester = tester
        self.verify_snapshot_view_page_loaded()

    _snapshot_view_page_title = "Snapshots"
    _create_snapshot_button_id = "create-snapshot-btn"
    _snapshot_action_menu_id = "table-item-dropdown_{0}"  #snapshot_id required
    _delete_snapshot_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(4)>a"  #snapshot_id required
    _view_details_actions_menu_item_css = "#item-dropdown_{0}>li>a"  #snapshot_id required
    _create_volume_from_snapshot_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(2)>a"  #snapshot_id required
    _register_as_image_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(3)>a"  #snapshot_id required
    _first_snapshot_link_in_list_css = "#tableview>table>tbody>tr>td>a"
    _snapshot_link_css = 'a[ng-href="/snapshots/{0}"]'  #snapshot_id required;
    _snapshot_status_xpath =  '//td/a[@href="/snapshots/{0}"]/../../td[2]' #snapshot_id required;
    _search_input_field_css = ".search-input"

    def verify_snapshot_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(ViewPage(self)._page_title_id, self._snapshot_view_page_title)
        self.tester.wait_for_visible_by_id(ViewPage(self)._refresh_button_id)

    def click_create_snapshot_btn_on_view_page(self):
        self.tester.click_element_by_id(self._create_snapshot_button_id)

    def click_action_delete_snapshot_on_view_page(self, snapshot_id):
        self.tester.click_element_by_id(ViewPage(self)._resource_action_menu_id.format(snapshot_id))
        self.tester.click_element_by_css(self._delete_snapshot_actions_menu_item_css.format(snapshot_id))

    def get_id_of_newly_created_snapshot(self, name=None):
        contains_id = self.tester.get_attrubute_by_css(self._first_snapshot_link_in_list_css, "ng-href")
        snapshot_id = contains_id[-13:]
        print(snapshot_id)
        return snapshot_id

    def verify_snapshot_status_is_completed(self, snapshot_id, timeout_in_seconds):
        self.tester.wait_for_text_present_by_xpath(self._snapshot_status_xpath.format(snapshot_id), "completed", timeout_in_seconds)

    def goto_snapshot_detail_page_via_link(self, snapshot_id):
        self.tester.click_element_by_css(self._snapshot_link_css.format(snapshot_id))

    def goto_snapshot_detail_page_via_actions(self, snapshot_id):
        self.tester.click_element_by_id(ViewPage(self)._resource_action_menu_id.format(snapshot_id))
        self.tester.click_element_by_css(self._view_details_actions_menu_item_css.format(snapshot_id))

    def click_action_create_volume_from_snapshot(self, snapshot_id):
        self.tester.click_element_by_id(ViewPage(self)._resource_action_menu_id.format(snapshot_id))
        self.tester.click_element_by_css(self._create_volume_from_snapshot_actions_menu_item_css.format(snapshot_id))

    def get_snapshot_name(self, snapshot_id):
        full_name = self.tester.store_text_by_css(self._snapshot_link_css.format(snapshot_id))
        snapshot_name=None
        if len(full_name)>16:
            snapshot_name = full_name[:-16]
        print snapshot_name
        return snapshot_name

    def click_action_register_as_image(self, snapshot_id):
        self.tester.click_element_by_id(ViewPage(self)._resource_action_menu_id.format(snapshot_id))
        self.tester.click_element_by_css(self._register_as_image_actions_menu_item_css.format(snapshot_id))

    def verify_there_are_no_completed_snapshots(self):
        self.tester.send_keys_by_css(ViewPage(self)._search_input_field_css, "completed")
        self.tester.wait_for_text_present_by_css(ViewPage(self)._item_count_css,"0")

    def verify_snapshot_not_present(self, snapshot_id):
        self.tester.wait_for_element_not_present_by_id(self._snapshot_action_menu_id.format(snapshot_id))
