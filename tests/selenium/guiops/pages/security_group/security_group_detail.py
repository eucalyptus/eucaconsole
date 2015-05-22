from pages.detailpage import DetailPage

class SecurityGroupDetailPage(DetailPage):

    def __init__(self, tester, s_group_name):
        self.s_group_name = s_group_name
        self.tester = tester
        self.verify_s_group_detail_page_loaded()

    _s_group_detail_page_title = "Details for security group: {0}"
    _delete_s_group_action_menuitem_id = "delete-securitygroup-action"
    _add_inbound_rules_protocol_menu_css = "a.chosen-single > span"
    _use_my_ip_address_link_id = "sgroup-use-my-ip"
    _add_rule_button_id = "button-add-rule"
    _save_changes_button_id = "save-securitygroup-btn"

    def verify_s_group_detail_page_loaded(self):
        """
        Waits for the security group detail page title to appear; waits for actions menu to become visible.
        :param s_group_name:
        """
        self.tester.wait_for_text_present_by_id(DetailPage._detail_page_title_id, self._s_group_detail_page_title.format(self.s_group_name))
        self.tester.wait_for_visible_by_css(DetailPage._actions_menu_css)

    def get_s_group_id(self):
        print "Getting security group id"
        url = self.tester.get_url()
        s_group_id = url[-11:]
        print "Security group id "+ s_group_id
        return s_group_id

    def click_action_delete_s_group_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_s_group_action_menuitem_id)

    def add_rule_to_s_group_open_to_my_ip(self):

        self.tester.click_element_by_css(self._add_inbound_rules_protocol_menu_css)
        self.tester.select_by_name_and_value("ip_protocol","3306")
        self.tester.click_element_by_id(self._use_my_ip_address_link_id)
        self.tester.click_element_by_id(self._add_rule_button_id)
        self.tester.click_element_by_id(self._save_changes_button_id)
