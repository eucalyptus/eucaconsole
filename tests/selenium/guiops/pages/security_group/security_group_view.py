from pages.viewpage import ViewPage

class SecurityGroupView(ViewPage):

    _s_group_view_page_title = "Security groups"
    _create_s_group_btn_id = "create-securitygroup-btn"
    _s_group_link_css = 'td>a:contains("{0}")'
    _s_group_actions_menu_id = "table-item-dropdown_{0}"
    _delete_keypair_actions_menuitem_css ="#item-dropdown_{0}>li>a"

    def __init__(self, tester):
        self.tester = tester
        self.verify_s_group_view_page_loaded()

    def verify_s_group_view_page_loaded(self):
        pass

    def get_s_group_id_from_view_page(self, s_group_name):
        pass


    def click_create_s_group_actions_menu(self):
        pass

    def click_action_delete_s_group_on_view_page(self, s_group_name):
        NotImplemented


    def click_action_view_s_group_details_on_view_page(self, s_group_name):
        NotImplementedError