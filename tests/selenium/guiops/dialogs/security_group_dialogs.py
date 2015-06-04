from pages.basepage import BasePage

class CreateScurityGroupDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _s_group_name_field_id = "name"
    _s_group_description_field = "description"
    _create_s_group_button_id = "create-securitygroup-btn"

    def create_s_group(self, s_group_name,  s_group_description):
        """
        Fills the s_group name and description fields. Clicks create s_group button.

        :param s_group_name:
        :param s_group_description:
        """
        self.tester.send_keys_by_id(self._s_group_name_field_id, s_group_name)
        self.tester.send_keys_by_id(self._s_group_description_field,  s_group_description)
        self.tester.click_element_by_id(self._create_s_group_button_id)

class DeleteScurityGroupDialog(BasePage):

    """
    Clicks the 'Yes, Delete' button in delete security group modal.
    """
    def __init__(self, tester):
        self.tester = tester

    _delete_s_group_submit_button_id = "delete_securitygroup_submit_button"

    def delete_s_group(self):
        self.tester.click_element_by_id(self._delete_s_group_submit_button_id)
