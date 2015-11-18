from pages.basepage import BasePage

class DeleteLaunchConfigModal(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_lc_submit_button_id = "delete_launchconfig_submit_button"

    def delete_launch_config(self):
        self.tester.click_element_by_id(self._delete_lc_submit_button_id)

