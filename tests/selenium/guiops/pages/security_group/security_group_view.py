from pages.viewpage import ViewPage

class SecurityGroupView(ViewPage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_s_group_view_page_loaded()

    def click_create_s_group_actions_menu(self):
        pass

    def click_action_delete_s_group_on_view_page(self, s_group_name):
        NotImplemented


    def click_action_view_s_group_details_on_view_page(self, s_group_name):
        NotImplementedError