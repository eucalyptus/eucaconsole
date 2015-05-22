from pages.viewpage import ViewPage

class SecurityGroupView(ViewPage):

    _s_group_view_page_title = "Security groups"
    _create_s_group_btn_id = "create-securitygroup-btn"
    _s_group_link_css = 'td>a:contains("{0}")'
    _s_group_actions_menu_id = "table-item-dropdown_{0}"
    _delete_s_group_actions_menuitem_css ="#item-dropdown_{0}>li:nth-child(2)>a"
    _view_details_actions_menuitem_css = "#item-dropdown_{0}>li>a"

    def __init__(self, tester):
        self.tester = tester
        self.verify_s_group_view_page_loaded()

    def verify_s_group_view_page_loaded(self):
        self.tester.wait_for_visible_by_id(self._create_s_group_btn_id)
        self.tester.wait_for_visible_by_id(self._refresh_button_id)

    def get_s_group_id_from_view_page(self, s_group_name):
        pass

    def click_create_new_s_group_button(self):
        self.tester.click_element_by_id(self._create_s_group_btn_id)

    def click_action_delete_s_group_on_view_page(self, s_group_id):
        self.tester.click_element_by_id(self._s_group_actions_menu_id.format(s_group_id))
        self.tester.click_element_by_css(self._delete_s_group_actions_menuitem_css.format(s_group_id))

    def click_action_view_s_group_details_on_view_page(self, s_group_id):
        self.tester.click_element_by_id(self._s_group_actions_menu_id.format(s_group_id))
        self.tester.click_element_by_css(self._view_details_actions_menuitem_css.format(s_group_id))

    def verify_s_group_not_present(self, s_group_name):
        self.tester.wait_for_element_not_present_by_css(self._s_group_link_css.format(s_group_name))

