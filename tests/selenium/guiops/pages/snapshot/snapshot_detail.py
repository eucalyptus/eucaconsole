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
        self.tester.wait_for_text_present_by_id(DetailPage(self)._detail_page_title_id, snapshot_name_full)
        self.tester.wait_for_element_present_by_css(DetailPage(self)._actions_menu_css)

    def click_action_delete_snapshot_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_snapshot_action_menuitem_id)

    def click_action_register_as_image_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._register_as_image_action_menuitem_id)

    def click_action_create_volume_from_snapshot_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._create_volume_from_snapshot_actions_menuitem_id)

    def verify_snapshot_status_is_completed(self, timeout_in_seconds):
        self.tester.wait_for_visible_by_css(self._snapshot_status_css.format("completed"), timeout_in_seconds)

    def get_snapshot_name_and_id(self, snapshot_name=None):
        name_and_id = str(self.tester.store_text_by_css(DetailPage(self)._resource_name_and_id_css))
        if snapshot_name is None:
            snapshot_id = name_and_id[-13:]
        else:
            snapshot_id = name_and_id[-14:-1]
        return {'snapshot_name': snapshot_name, 'snapshot_id': snapshot_id}


