from pages.landingpage import LandingPage


class StacksLandingPage(LandingPage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_stacks_lp_loaded()

    _stacks_lp_title = "Stacks"
    _create_stack_btn_id = "create-stack-btn"
    _stack_link_css = 'a[href="/stacks/{0}"]'
    _stack_actions_menu_id = "table-item-dropdown_{0}"
    _view_details_stack_actions_menuitem_css ="#item-dropdown_{0}>li>a"
    _update_stack_actions_menuitem_css ="#item-dropdown_{0}>li:nth-of-type(2)>a"
    _delete_stack_actions_menuitem_css ="#item-dropdown_{0}>li:nth-of-type(3)>a"

    def verify_stacks_lp_loaded(self):
        """
        Waits for page title to load; waits for refresh button to load; wait for 'Create Stack' button to load.
        """
        self.tester.wait_for_text_present_by_id(LandingPage._page_title_id, self._stacks_lp_title)
        self.tester.wait_for_visible_by_id(LandingPage._refresh_button_id)
        self.tester.wait_for_visible_by_id(self._create_stack_btn_id)

    def click_create_stack_button_on_landing_page(self):
        """
        Clicks "Create Stacks" button on Stacks landing page.
        """
        self.tester.click_element_by_id(self._create_stack_btn_id)

    def click_stack_link_on_landing_page(self, stack_name):
        """
        Clicks link of a given stack on Stacks landing page.
        :param stack_name:
        """
        self.tester.click_element_by_css(self._stack_link_css.format(stack_name))

    def verify_stack_present_on_landing_page(self, stack_name):
        """
        Verifies that stack link is present on Stacks landing page.
        :param stack_name:
        """
        self.tester.wait_for_element_present_by_css(self._stack_link_css.format(stack_name))

    def verify_stack_not_present_on_landing_page(self, stack_name):
        """
        Verifies that stack link is not present on Stacks landing page.
        :param stack_name:
        """
        self.tester.wait_for_element_not_present_by_css(self._stack_link_css.format(stack_name))

    def click_action_view_stack_details_on_landing_page(self, stack_name):
        """
        Clicks action menu for a given stack on Stacks landing page. Clicks "View Stack" action.
        :param stack_name:
        """
        self.tester.click_element_by_id(self._stack_actions_menu_id.format(stack_name))
        self.tester.click_element_by_css(self._view_details_stack_actions_menuitem_css.format(stack_name))

    def click_action_update_stack_on_landing_page(self, stack_name):
        """
        Clicks action menu for a given stack on Stacks landing page. Clicks "Update Stack" action.
        :param stack_name:
        """
        self.tester.click_element_by_id(self._stack_actions_menu_id.format(stack_name))
        self.tester.click_element_by_css(self._update_stack_actions_menuitem_css.format(stack_name))

    def click_action_delete_stack_on_landing_page(self, stack_name):
        """
        Clicks action menu for a given stack on Stacks landing page. Clicks "Delete Stack" action.
        :param stack_name:
        """
        self.tester.click_element_by_id(self._stack_actions_menu_id.format(stack_name))
        self.tester.click_element_by_css(self._delete_stack_actions_menuitem_css.format(stack_name))
