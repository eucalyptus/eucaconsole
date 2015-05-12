from pages.basepage import BasePage

class CreateKeypairDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _keypair_name_field_id="key-name"
    _create_and_download_button_css="button.button"

    def create_keypair(self,keypair_name):
        self.tester.send_keys_by_id(self._keypair_name_field_id, keypair_name)
        self.tester.click_element_by_css(self._create_and_download_button_css)



