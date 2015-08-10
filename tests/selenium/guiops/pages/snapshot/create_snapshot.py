from pages.detailpage import BasePage
from string import split

class CreateSnapshotPage(BasePage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_create_snapshot_page_loaded()

    _page_title = "Create new snapshot"
    _name_input_field_id = "name"
    _volume_selector_css = '[class="chosen-single"]>span'
    _volume_selector_search_window_css = '.chosen-search>input'
    _highlighted_search_result_css = '.active-result'
    _description_field_id = 'description'
    _create_snapshot_submit_button_id = "create_snapshot_submit_button"

    def verify_create_snapshot_page_loaded(self):
        self.tester.wait_for_text_present_by_id(BasePage(self)._page_title_id, self._page_title)
        self.tester.wait_for_element_present_by_id(self._name_input_field_id)

    def create_snapshot(self, volume_id, snapshot_name=None, snapshot_description=None, timeout_in_seconds=240):
        if snapshot_name is not None:
            self.tester.send_keys_by_id(self._name_input_field_id, snapshot_name)
        self.tester.click_element_by_css(self._volume_selector_css)
        self.tester.send_keys_by_css(self._volume_selector_search_window_css, volume_id)
        self.tester.click_element_by_css(self._highlighted_search_result_css)
        self.tester.click_element_by_id(self._create_snapshot_submit_button_id)



