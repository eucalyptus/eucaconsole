from pages.detailpage import DetailPage

class StackDetailPage(DetailPage):

    def __init__(self, tester, stack_name=None):
        self.stack_name = stack_name
        self.tester = tester


    _stack_detail_page_title = "Details for stack: {0}"
    _delete_stack_action_menuitem_id = "delete-stack-action"

    def verify_stack_detail_page_loaded(self):
        """
        Waits for the stack detail page title to appear; waits for actions menu to become visible.
        """
        self.tester.wait_for_text_present_by_id(DetailPage._detail_page_title_id, self._stack_detail_page_title.format(self.stack_name))
        self.tester.wait_for_visible_by_css(DetailPage._actions_menu_css)

    def click_action_delete_stack_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_stack_action_menuitem_id)

