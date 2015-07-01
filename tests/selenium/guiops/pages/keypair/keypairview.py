from pages.viewpage import ViewPage

class KeypairView(ViewPage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_keypair_view_page_loaded()

    _keypair_view_page_title = "Key Pairs"
    _create_keypair_btn_id = "create-keypair-btn"
    _split_button_css =".euca-split"
    _import_keypair_btn_id = "import-keypair-btn"
    _keypair_link_css = 'td>a[href="/keypairs/{0}"]'
    _keypair_actions_menu_id = "table-item-dropdown_{0}"
    _delete_keypair_actions_menuitem_css ="#item-dropdown_{0}>li>a"

    def verify_keypair_view_page_loaded(self):
        """
        Waits for page title to load; waits for refresh button to load; wait for 'Create New Key Pair' button to load.
        """
        self.tester.wait_for_text_present_by_id(ViewPage._page_title_id, self._keypair_view_page_title)
        self.tester.wait_for_visible_by_id(ViewPage._refresh_button_id)
        self.tester.wait_for_visible_by_id(self._create_keypair_btn_id)

    def click_create_keypair_button_on_view_page(self):
        self.tester.click_element_by_id(self._create_keypair_btn_id)

    def click_import_keypair_button(self):
        self.tester.click_element_by_css(self._split_button_css)
        self.tester.click_element_by_id(self._import_keypair_btn_id)

    def click_keypair_link_on_view_page(self, keypair_name):
        self.tester.click_element_by_css(self._keypair_link_css.format(keypair_name))

    def verify_keypair_present_on_view_page(self, keypair_name):
        self.tester.wait_for_element_present_by_css(self._keypair_link_css.format(keypair_name))

    def verify_keypair_not_present_on_view_page(self, keypair_name):
        self.tester.wait_for_element_not_present_by_css(self._keypair_link_css.format(keypair_name))

    def click_action_delete_keypair_on_view_page(self, keypair_name):
        self.tester.click_element_by_id(self._keypair_actions_menu_id.format(keypair_name))
        self.tester.click_element_by_css(self._delete_keypair_actions_menuitem_css.format(keypair_name))



