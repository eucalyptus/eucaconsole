import time

from pages.landingpage import LandingPage


class VolumeLanding(LandingPage):
    def __init__(self, tester):
        self.tester = tester
        self.print_test_context()
        self.verify_volume_view_page_loaded()

    _volume_view_page_title = "Volumes"
    _create_volume_button_id = "create-volume-btn"
    _volume_action_menu_id = "table-item-dropdown_{0}"  # volume_id required
    _delete_volume_actions_menu_item_css = "#item-dropdown_{0} .delete-volume-action"  # volume_id required
    _detach_volume_actions_menu_item_css = "#item-dropdown_{0} .detach-volume-action"  # volume_id required
    _view_details_actions_menu_item_css = "#item-dropdown_{0}>li>a"  # volume_id required
    _manage_snapshots_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(2)>a"  # volume_id required
    _attach_to_instance_actions_menu_item_css = "#item-dropdown_{0} .attach-volume-action"  # volume_id required
    _first_volume_link_in_list_css = "#tableview>table>tbody>tr>td>a"
    _volume_link_css = "#table-id-column-{0}>a"  # volume_id required;
    _volume_status_css = '#tableview [data-item-id="{0}"] td.status'  # volume_id required;
    _search_input_field_css = ".search-input"
    _sortable_column_header_css = '#tableview .table thead th[st-sort="{0}"]'  # requires column name;
    _sortable_row_by_position_xpath = '//div[@id="tableview"]/table/tbody/tr[{0}]'  # requires position
    _sortable_row_with_expandos_by_position_xpath = '//div[@id="tableview"]/table/tbody[{0}]'  # requires position

    def verify_volume_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(LandingPage(self)._page_title_id, self._volume_view_page_title)
        self.tester.wait_for_visible_by_id(LandingPage(self)._refresh_button_id)

    def click_create_volume_btn_on_landing_page(self):
        self.tester.click_element_by_id(self._create_volume_button_id)

    def click_action_delete_volume_on_view_page(self, volume_id):
        self.tester.click_element_by_id(self._volume_action_menu_id.format(volume_id))
        self.tester.click_element_by_css(self._delete_volume_actions_menu_item_css.format(volume_id))

    def click_action_detach_volume_on_view_page(self, volume_id):
        self.tester.click_element_by_id_css_robust(self._volume_action_menu_id.format(volume_id), self._detach_volume_actions_menu_item_css.format(volume_id))
        self.tester.click_element_by_css(self._detach_volume_actions_menu_item_css.format(volume_id))

    def get_id_of_newly_created_volume(self, name=None):
        contains_id = self.tester.get_attribute_by_css(self._first_volume_link_in_list_css, "ng-href")
        volume_id = contains_id[-12:]
        print(volume_id)
        return volume_id

    def verify_volume_status_is_available(self, volume_id, timeout_in_seconds):
        self.tester.wait_for_text_present_by_css(self._volume_status_css.format(volume_id), "available", timeout_in_seconds)

    def verify_volume_status_is_deleted(self, volume_id, timeout_in_seconds):
        # Note: Deleted volumes are filtered out from the landing page as of the 4.2 release of the console
        self.tester.wait_for_element_not_present_by_css(self._volume_link_css.format(volume_id), timeout_in_seconds)

    def verify_volume_status_is_attached(self, volume_id, timeout_in_seconds):
        self.tester.wait_for_text_present_by_css(self._volume_status_css.format(volume_id), "attached", timeout_in_seconds)

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
        self.tester.wait_for_text_present_by_css(LandingPage(self)._item_count_css, "0", timeout_in_seconds)

    def click_sortable_column_header(self, column_name='name'):
        self.tester.click_element_by_css(self._sortable_column_header_css.format(column_name))

    def verify_volume_id_by_sort_position(self, volume_id, position=1):
        """
        :param volume_id:
        :param position: sorting position. Note: not zero-based (e.g. use 1 for first row)
        :type position: int
        """
        selector = self._sortable_row_by_position_xpath.format(position)
        time.sleep(1)
        self.tester.wait_for_visible_by_xpath(selector)
        assert volume_id == self.tester.get_attribute_by_xpath(selector, 'data-item-id')
