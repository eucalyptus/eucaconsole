from pages.basepage import BasePage

class CreateNewSnapshotDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

        NotImplementedError


class CreateSnapshotModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _snapshot_name_field_id = "name"
    _snapshot_description_field_id = "description"
    _create_snapshot_submit_button_css = '[class="button expand"]'

    def create_snapshot(self, snapshot_name=None, snapshot_description=None):
        if snapshot_name is not None:
            self.tester.send_keys_by_id(self._snapshot_name_field_id, snapshot_name)
        if snapshot_description is not None:
            self.tester.send_keys_by_id(self._snapshot_description_field_id, snapshot_description)
        self.tester.click_element_by_css(self._create_snapshot_submit_button_css)


class DeleteSnapshotModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_snapshot_submit_button_id = "delete_snapshot_submit_button"

    def delete_snapshot(self):
        self.tester.click_element_by_id(self._delete_snapshot_submit_button_id)
