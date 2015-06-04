from pages.basepage import BasePage

class CreateKeypairDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _keypair_name_field_id = "key-name"
    _create_and_download_button_css="button.button"

    def create_keypair(self,keypair_name):
        self.tester.send_keys_by_id(self._keypair_name_field_id, keypair_name)
        self.tester.click_element_by_css(self._create_and_download_button_css)

class ImportKeypairDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _keypair_name_field_id = "key-name"
    _ssh_key_contents_field_id = "key-import-contents"
    _import_keypair_submit_button_css = "button.button"


    def import_keypair(self, keypair, keypair_name):
        self.tester.send_keys_by_id(self._keypair_name_field_id, keypair_name)
        self.tester.send_keys_by_id(self._ssh_key_contents_field_id, keypair)
        self.tester.wait_for_clickable_by_css(self._import_keypair_submit_button_css)
        self.tester.click_element_by_css(self._import_keypair_submit_button_css)

class DeleteKeypairModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_keypair_submit_button_id = "delete_keypair_submit_button"

    def click_delete_keypair_submit_button(self):
        self.tester.click_element_by_id(self._delete_keypair_submit_button_id)

class CreateKeypairModal(BasePage):
    pass

