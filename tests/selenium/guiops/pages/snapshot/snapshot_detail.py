from pages.detailpage import DetailPage

class SnapshotDetailPage(DetailPage):

    def __init__(self, tester):
        self.tester = tester

    _snapshot_detail_page_title = "Details for snapshot: {0}"  # snapshot name and id required
    _delete_snapshot_action_menuitem_id = "delete-snapshot-action"
    _register_as_image_action_menuitem_id = "register-snapshot-action"
    _create_volume_from_snapshot_actions_menuitem_id ="create-volume-action"
    _snapshot_status_css = "[class='label radius status {0}']"  # snapshot status is required

    def verify_snapshot_detail_page_loaded(self, snapshot_id, snapshot_name):
        """
        Waits for the snapshot detail page title to appear; waits for actions menu to become visible.
        :param snapshot_id:
        :param snapshot_name:
        """
        if snapshot_name is None:
            snapshot_name_full = snapshot_id
        else:
            snapshot_name_full = snapshot_name + " (" + snapshot_id + ")"
        self.tester.wait_for_text_present_by_id(DetailPage(self)._detail_page_title_id, volume_name_full)
        self.tester.wait_for_element_present_by_css(DetailPage(self)._actions_menu_css)

    def click_action_delete_volume_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_volume_action_menuitem_id)

    def click_action_attach_volume_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._attach_volume_action_menuitem_id)

    def verify_volume_status_is_available(self):
        self.tester.wait_for_visible_by_css(self._volume_status_css.format("available"))

    def verify_volume_status_is_attached(self):
        self.tester.wait_for_visible_by_css(self._volume_status_css.format("attached"))

    def get_volume_name_and_id(self):
        name_and_id = str(self.tester.store_text_by_css(DetailPage(self)._resource_name_and_id_css))
        volume_id = name_and_id[-13:-1]
        volume_name = name_and_id[1:-15]
        return {'volume_name': volume_name, 'volume_id': volume_id}


