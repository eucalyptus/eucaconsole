from pages.basepage import BasePage

class CreateVolumeDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _volume_name_field_id = "name"
    _create_from_snapshot_id = "snapshot_id_chosen"
    _create_from_snapshot_search_field_css = ".chosen-search>input"
    _volume_size_field_id = "size"
    _availability_zone_selector_id ="zone"
    _create_volume_submit_button_id = "create_volume_submit_button"

    def create_volume(self, volume_name=None, create_from_snapshot=False, snapshot_id = None, volume_size=None, availability_zone=None):
        if volume_name is not None:
            self.tester.send_keys_by_id(self._volume_name_field_id, volume_name)
        if create_from_snapshot:
            self.tester.click_element_by_id(self._create_from_snapshot_id)
            self.tester.send_keys_by_css(self._create_from_snapshot_search_field_css, snapshot_id)
        if availability_zone is not None:
            self.tester.select_by_id(self._availability_zone_selector_id, availability_zone)
        if volume_size is not None:
            self.tester.send_keys_by_id(self._volume_size_field_id, volume_size)
        self.tester.click_element_by_id(self._create_volume_submit_button_id)

class DeleteVolumeModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_volume_submit_button_id = "delete_volume_submit_button"

    def delete_volume(self):
        self.tester.click_element_by_id(self._delete_volume_submit_button_id)
