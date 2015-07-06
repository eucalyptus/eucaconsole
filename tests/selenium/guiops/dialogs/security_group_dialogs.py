from pages.basepage import BasePage

class CreateScurityGroupDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _s_group_name_field_id = "name"
    _s_group_description_field = "description"
    _create_s_group_button_id = "create-securitygroup-btn"
    _add_inbound_rules_protocol_menu_id = "ip_protocol_select_chosen"
    _inbound_rules_text_input_field_css = "#ip_protocol_select_chosen>.chosen-drop>.chosen-search>input[type='text']"
    _open_to_all_addresses_link_id = "sgroup-use-my-ip"
    _rule_assignment_port_begin_css = "[class='port from ng-pristine ng-untouched ng-valid ng-valid-pattern']"
    _rule_assignment_port_end_css = "[class='port to ng-pristine ng-untouched ng-valid ng-valid-pattern']"
    _add_rule_button_id = "button-add-rule"
    _security_group_radio_button_css = ".securitygroupname>input[type='radio']"
    _groupname_selection_menu_css = "#groupname_select_chosen>a"
    _groupname_selection_search_css = "#groupname_select_chosen>div>div>input"

    def create_s_group(self, s_group_name,  s_group_description):
        """
        Fills the s_group name and description fields. Clicks create s_group button.

        :param s_group_name:
        :param s_group_description:
        """
        self.tester.send_keys_by_id(self._s_group_name_field_id, s_group_name)
        self.tester.send_keys_by_id(self._s_group_description_field,  s_group_description)
        self.tester.click_element_by_id(self._create_s_group_button_id)

    def create_s_group_with_rules(self, s_group_name, s_group_description, rule_open_to_all, rule_open_to_default_group, rule_open_to_default_group_port_begin, rule_open_to_default_group_port_end):
        """
        Creates security group with one rule open to all, and one custom rule open to default group.
        :param s_group_name:
        :param s_group_description:
        :param rule_open_to_all:
        :param rule_open_to_default_group:
        :param rule_open_to_default_group_port_begin:
        :param rule_open_to_default_group_port_end:
        """
        self.tester.send_keys_by_id(self._s_group_name_field_id, s_group_name)
        self.tester.send_keys_by_id(self._s_group_description_field,  s_group_description)
        self.tester.click_element_by_id(self._add_inbound_rules_protocol_menu_id)
        self.tester.send_keys_by_css(self._inbound_rules_text_input_field_css, rule_open_to_all)
        self.tester.click_element_by_css(".active-result")
        self.tester.click_element_by_id(self._open_to_all_addresses_link_id)
        self.tester.click_element_by_id(self._add_rule_button_id)
        self.tester.click_element_by_id(self._add_inbound_rules_protocol_menu_id)
        self.tester.send_keys_by_css(self._inbound_rules_text_input_field_css, rule_open_to_default_group)
        self.tester.click_element_by_css(".active-result")
        self.tester.send_keys_by_css(self._rule_assignment_port_begin_css, rule_open_to_default_group_port_begin)
        self.tester.send_keys_by_css(self._rule_assignment_port_end_css, rule_open_to_default_group_port_end)
        self.tester.click_element_by_css(self._security_group_radio_button_css)
        self.tester.click_element_by_css(self._groupname_selection_menu_css)
        self.tester.send_keys_by_css(self._groupname_selection_search_css, "default")
        self.tester.click_element_by_css('[class="active-result ng-binding ng-scope highlighted"]')
        self.tester.click_element_by_id(self._add_rule_button_id)
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
