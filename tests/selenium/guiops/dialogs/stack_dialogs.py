from pages.basepage import BasePage

class DeleteStackDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_stack_submit_button_id = "delete_stack_submit_button"

    def delete_stack(self):
        self.tester.click_element_by_id(self._delete_stack_submit_button_id)

