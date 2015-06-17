from pages.viewpage import ViewPage


class VolumeView(ViewPage):
    def __init__(self, tester):
        self.tester = tester
        self.verify_volume_view_page_loaded()

    _volume_view_page_title = "Volumes"
    _create_volume_button_id = "create-volume-btn"
    _volume_action_menu_id = "table-item-dropdown_{0}"  #volume_id required
    _delete_volume_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(5)>a"  #volume_id required
    _view_details_actions_menu_item_css = "#item-dropdown_{0}>li>a"  #ivolume_id required
    _manage_snapshots_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(2)>a"  #volume_id required
    _attach_to_instance_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(3)>a"  #volume_id required
    _first_volume_link_in_list_css = "#tableview>table>tbody>tr>td>a"
    _volume_link_css = 'a[ng-href="/volumes/{0}"]'  #volume_id required;
    _volume_status_xpath =  '//td/a[@href="/volumes/{0}"]/../../td[2]' #volume_id required;
    _search_input_field_css = ".search-input"

    def verify_volume_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(ViewPage(self)._page_title_id, self._volume_view_page_title)
        self.tester.wait_for_visible_by_id(ViewPage(self)._refresh_button_id)

    def click_create_volume_btn_on_view_page(self):
        self.tester.click_element_by_id(self._create_volume_button_id)

    def click_action_delete_volume_on_view_page(self, volume_id):
        self.tester.click_element_by_id(self._volume_action_menu_id.format(volume_id))
        self.tester.click_element_by_css(self._delete_volume_actions_menu_item_css.format(volume_id))

    def get_id_of_newly_created_volume(self, name=None):
        contains_id = self.tester.get_attrubute_by_css(self._first_volume_link_in_list_css, "ng-href")
        volume_id = contains_id[-12:]
        print(volume_id)
        return volume_id

    def verify_volume_status_is_available(self, volume_id, timeout_in_seconds):
        self.tester.wait_for_text_present_by_xpath(self._volume_status_xpath.format(volume_id), "available", timeout_in_seconds)

    def verify_volume_status_is_deleted(self, volume_id, timeout_in_seconds):
        self.tester.wait_for_text_present_by_xpath(self._volume_status_xpath.format(volume_id), "deleted", timeout_in_seconds)

    def goto_volume_detail_page_via_link(self, volume_id):
        self.tester.click_element_by_css(self._volume_link_css.format(volume_id))

    def goto_volume_detail_page_via_actions(self, volume_id):
        self.tester.click_element_by_id(self._volume_action_menu_id.format(volume_id))
        self.tester.click_element_by_css(self._view_details_actions_menu_item_css.format(volume_id))

    def click_action_manage_snaspshots(self, volume_id):
        self.tester.click_element_by_id(self._volume_action_menu_id.format(volume_id))
        self.tester.click_element_by_css(self._manage_snapshots_actions_menu_item_css.format(volume_id))

    def get_volume_name(self, volume_id):
        full_name = self.tester.store_text_by_css(self._volume_link_css.format(volume_id))
        volume_name=None
        if len(full_name)>14:
            volume_name = full_name[:-14]
        return volume_name

    def click_action_attach_to_instance(self, volume_id):
        self.tester.click_element_by_id(self._volume_action_menu_id.format(volume_id))
        self.tester.click_element_by_css(self._attach_to_instance_actions_menu_item_css.format(volume_id))

    def verify_there_are_no_available_volumes(self, timeout_in_seconds):
        self.tester.send_keys_by_css(self._search_input_field_css, "available")
        self.tester.wait_for_text_present_by_css(ViewPage(self)._item_count_css, "0", timeout_in_seconds)
