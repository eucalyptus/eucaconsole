from pages.detailpage import DetailPage

class SecurityGroupDetailPage(DetailPage):

    def __init__(self, tester, s_group_name):
        self.s_group_name = s_group_name
        self.tester = tester
        self.verify_s_group_detail_page_loaded()

    _s_group_detail_page_title = "Details for security group: {0}"
    _delete_s_group_action_menuitem_id = "delete-securitygroup-action"

    def verify_s_group_detail_page_loaded(self):
        """
        Waits for the security group detail page title to appear; waits for actions menu to become visible.
        :param s_group_name:
        """
        self.tester.wait_for_text_present_by_id(DetailPage._detail_page_title_id, self._s_group_detail_page_title.format(self.s_group_name))
        self.tester.wait_for_visible_by_css(DetailPage._actions_menu_css)

    def click_action_delete_s_group_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_s_group_action_menuitem_id)
