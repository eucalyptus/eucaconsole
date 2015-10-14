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

    def create_volume(self, volume_name=None, create_from_snapshot=False, snapshot_id = None, volume_size=None, availability_zone=None, timeout_in_seconds=120):
        if volume_name is not None:
            self.tester.send_keys_by_id(self._volume_name_field_id, volume_name)
        if create_from_snapshot:
            self.tester.click_element_by_id(self._create_from_snapshot_id)
            self.tester.send_keys_by_css(self._create_from_snapshot_search_field_css, snapshot_id)
        if availability_zone is not None:
            self.tester.select_by_id(self._availability_zone_selector_id, availability_zone, timeout_in_seconds=timeout_in_seconds)
        if volume_size is not None:
            self.tester.send_keys_by_id(self._volume_size_field_id, volume_size)
        self.tester.click_element_by_id(self._create_volume_submit_button_id)

class DeleteVolumeModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_volume_submit_button_id = "delete_volume_submit_button"

    def delete_volume(self):
        self.tester.click_element_by_id(self._delete_volume_submit_button_id)

class AttachVolumeModalSelectInstance(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _instance_dropdown_css = ".chosen-single"
    _search_field_css = ".chosen-search>input"
    _active_result_css = ".active-result"
    _device_field_id = "device"
    _attach_volume_submit_button_id = "attach_volume_submit_button"

    def attach_volume(self, instance_id, device=None):
        self.tester.click_element_by_css(self._instance_dropdown_css)
        self.tester.send_keys_by_css(self._search_field_css, instance_id)
        self.tester.click_element_by_css(self._active_result_css)
        if device is not None:
            self.tester.send_keys_by_id(self._device_field_id, device)
        self.tester.click_element_by_id_robust(self._attach_volume_submit_button_id)

class AttachVolumeModalSelectVolume(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _volume_dropdown_css = ".chosen-single"
    _search_field_css = ".chosen-search>input"
    _active_result_css = ".active-result"
    _device_field_id = "device"
    _attach_volume_submit_button_css = '#attach-volume-modal>form>div>div>input[class="button expand"]'

    def attach_volume(self, volume_id, device=None):
        self.tester.click_element_by_css(self._volume_dropdown_css)
        self.tester.send_keys_by_css(self._search_field_css, volume_id)
        self.tester.click_element_by_css(self._active_result_css)
        if device is not None:
            self.tester.send_keys_by_id(self._device_field_id, device)
        self.tester.click_element_by_css(self._attach_volume_submit_button_css)


class DetachVolumeModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _detach_volume_submit_button_id = "detach_volume_submit_button"
    _volume_id_in_the_message_css = "span>b"
    _volume_id_in_the_message_xpath= '//div[@id="detach-volume-modal"]/p[2]/span[2]'

    def detach_volume(self, volume_id):
        self.tester.wait_for_text_present_by_xpath(self._volume_id_in_the_message_xpath, volume_id)
        self.tester.click_element_by_id(self._detach_volume_submit_button_id)


