from pages.detailpage import DetailPage


class StackDetailPage(DetailPage):

    def __init__(self, tester, stack_name):
        """
        Initiates Stack Detail page object.
        :param tester:
        :param stack_name:
        """
        self.stack_name = stack_name
        self.tester = tester
        self.verify_stack_detail_page_loaded()

    _stack_detail_page_title = 'Details for stack: {0}'
    _delete_stack_action_menuitem_id = 'delete-stack-action'
    _template_tab_css ='.tabs>dd:nth-of-type(2)>a'
    _events_tab_css ='.tabs>dd:nth-of-type(3)>a'
    _create_complete_status_css = "div>span.Create-complete"
    _update_complete_status_css = "div>span.Update-complete"

    def verify_stack_detail_page_loaded(self):
        """
        Waits for the stack detail page title to appear; waits for actions menu to become visible.
        """
        self.tester.wait_for_text_present_by_id(DetailPage._detail_page_title_id, self._stack_detail_page_title.format(self.stack_name))
        self.tester.wait_for_visible_by_css(DetailPage._actions_menu_css)

    def click_action_delete_stack_on_detail_page(self):
        """
        Clicks "Actions" button on Stacks Detail page. Clicks "Delete Stack" action.
        """
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_stack_action_menuitem_id)

    def click_tab_template_on_detail_page(self):
        """
        Clicks "Template" tab on Stacks Detail page.
        """
        self.tester.click_element_by_css(self._template_tab_css)

    def click_tab_events_on_detail_page(self):
        """
        Clicks "Events" tab on Stacks Detail page.
        """
        self.tester.click_element_by_css(self._events_tab_css)

    def wait_for_create_complete(self):
        """
        Waits for stack status to be "Create complete"
        """
        self.tester.wait_for_visible_by_css(self._create_complete_status_css)

    def wait_for_update_complete(self):
        """
        Waits for stack status to be "Create complete"
        """
        self.tester.wait_for_visible_by_css(self._update_complete_status_css)
