from pages.basepage import BasePage

class DeleteKeypairModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_keypair_submit_button_id = "delete_keypair_submit_button"

    def click_delete_keypair_submit_button(self):
        self.tester.click_element_by_id(self._delete_keypair_submit_button_id)