from pages.basepage import BasePage

class CreateNewSnapshotDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

        NotImplementedError


class CreateSnapshotModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _snapshot_name_field_xpath = "(//input[@id='name'])[2]"
    _snapshot_description_field_xpath = "(//textarea[@id='description'])[2]"
    _create_snapshot_submit_button_css = "input.button.expand"

    def create_snapshot(self, snapshot_name=None, snapshot_description=None):
        if snapshot_name is not None:
            self.tester.send_keys_by_xpath(self._snapshot_name_field_xpath, snapshot_name)
        if snapshot_description is not None:
            self.tester.send_keys_by_xpath(self._snapshot_description_field_xpath, snapshot_description)
        self.tester.click_element_by_css(self._create_snapshot_submit_button_css)


class DeleteSnapshotModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_snapshot_submit_button_id = "delete_snapshot_submit_button"

    def delete_snapshot(self):
        self.tester.click_element_by_id(self._delete_snapshot_submit_button_id)


class RegisterSnapshotAsImageModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _name_field_css = "#register-snapshot-modal #controls_name #name"
    _description_field_id = "description"
    _delete_on_terminate_checkbox_id = "dot"
    _register_as_windows_image_checkbox_id = "reg_as_windows"
    _register_as_image_submit_button_id = "register_snapshot_submit_button"

    def register_as_image(self, name, description=None, delete_on_terminate=True, register_as_windows_image=False):

        self.tester.send_keys_by_css(self._name_field_css, name)
        if description is not None:
            self.tester.send_keys_by_id(self._description_field_id, description)
        if delete_on_terminate is False:
            self.tester.click_element_by_id(self._delete_on_terminate_checkbox_id)
        if register_as_windows_image:
            self.tester.click_element_by_id(self._register_as_windows_image_checkbox_id)
        self.tester.click_element_by_id(self._register_as_image_submit_button_id)





