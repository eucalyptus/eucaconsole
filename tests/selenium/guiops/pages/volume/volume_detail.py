from pages.detailpage import DetailPage

class VolumeDetailPage(DetailPage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_volume_detail_page_loaded()

    _volume_detail_page_title = "Details for volume: {0}"
    _delete_volume_action_menuitem_id = "delete-volume-action"
    _attach_volume_action_menuitem_id = "attach-volume-action"
    _volume_status_css = "[class='label radius status {0}']" #volume status is required

    def verify_volume_detail_page_loaded(self, volume_id, volume_name):
        """
        Waits for the volume detail page title to appear; waits for actions menu to become visible.
        """
        if volume_name is None:
            volume_name_full = volume_id
        else:
            volume_name_full = volume_name + " (" + volume_id + ")"
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


