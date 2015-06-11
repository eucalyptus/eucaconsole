from pages.detailpage import DetailPage

class VolumeDetailPage(DetailPage):

    def __init__(self, tester, volume_id, volume_name):
        self.volume_id = volume_id
        self.volume_name = volume_name
        self.tester = tester
        self.verify_volume_detail_page_loaded()

    _volume_detail_page_title = "Details for key pair: {0}"
    _delete_volume_action_menuitem_id = "delete-keypair-action"

    def verify_volume_detail_page_loaded(self):
        """
        Waits for the volume detail page title to appear; waits for actions menu to become visible.
        """
        self.tester.wait_for_text_present_by_id(DetailPage._detail_page_title_id, self._keypair_detail_page_title.format(self.keypair_name))
        self.tester.wait_for_visible_by_css(DetailPage._actions_menu_css)

    def click_action_delete_volume_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_volume_action_menuitem_id)


