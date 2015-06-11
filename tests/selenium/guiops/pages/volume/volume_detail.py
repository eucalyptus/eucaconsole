from pages.detailpage import DetailPage

class VolumeDetailPage(DetailPage):

    def __init__(self, tester, volume_id, volume_name):
        self.volume_id = volume_id
        self.volume_name = volume_name
        self.tester = tester
        self.verify_volume_detail_page_loaded()

    _volume_detail_page_title = "Details for volume: {0}"
    _delete_volume_action_menuitem_id = "delete-volume-action"
    _attach_volume_action_menuitem_id = "attach-volume-action"

    def verify_volume_detail_page_loaded(self):
        """
        Waits for the volume detail page title to appear; waits for actions menu to become visible.
        """
        if self.volume_name is None:
            volume_name_full = self.volume_id
        else:
            volume_name_full = self.volume_name + " (" + self.volume_id + ")"
        self.tester.wait_for_text_present_by_id(DetailPage(self)._detail_page_title_id, volume_name_full)
        self.tester.wait_for_element_present_by_css(DetailPage(self)._actions_menu_css)

    def click_action_delete_volume_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_volume_action_menuitem_id)

    def click_action_attach_volume_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._attach_volume_action_menuitem_id)

