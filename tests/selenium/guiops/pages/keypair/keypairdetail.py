from pages.detailpage import DetailPage

class KeypairDetailPage(DetailPage):

    def __init__(self, tester):
        self.tester = tester

    _keypair_detail_page_title = "Details for key pair"

    def verify_keypair_detail_page_loaded(self):
        """
        Waits for the keypair detail page title to appear; waits for actions menu to become visible.
        """
        self.tester.wait_for_text_present_by_id(DetailPage._detail_page_title_id, self._keypair_detail_page_title)
        self.tester.wait_for_visible_by_css(DetailPage._actions_menu_css)

