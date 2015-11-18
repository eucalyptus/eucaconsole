from pages.basepage import BasePage

class DeleteASGModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_asg_submit_button_id = "delete_scalinggroup_submit_button"

    def delete_asg(self):
        self.tester.click_element_by_id(self._delete_asg_submit_button_id)

