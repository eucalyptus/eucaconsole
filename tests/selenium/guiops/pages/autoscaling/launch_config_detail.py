from pages.detailpage import DetailPage


class LaunchConfigDetailPage(DetailPage):

    def __init__(self, tester):
        self.tester = tester

    _lc_detail_page_title = "Details for launch configuration: {0}" #lc name required
    _delete_lc_action_menuitem_id = "delete-launchconfig-action"
    _create_lc_like_this_action_menuitem_id = "create-another-launchconfig-action"
    _create_asg_action_menuitem_id = "create-scalinggroup-action"


    def verify_lc_detail_page_loaded(self, lc_name):
        """
        Waits for the lc detail page title to appear; waits for actions menu to become visible.
        """
        self.tester.wait_for_text_present_by_id(DetailPage(self)._detail_page_title_id, self._lc_detail_page_title.format(lc_name))
        self.tester.wait_for_element_present_by_css(DetailPage(self)._actions_menu_css)

    def click_action_delete_lc_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_lc_action_menuitem_id)

    def create_lc_like_this_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._create_lc_like_this_action_menuitem_id)

    def create_asg_on_lc_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._create_asg_action_menuitem_id)









