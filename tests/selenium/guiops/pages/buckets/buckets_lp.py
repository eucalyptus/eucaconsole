from pages.landingpage import LandingPage


class BucketsView(LandingPage):

    def __init__(self, tester):
        super(BucketsView, self).__init__(tester)

    _page_title = "Buckets"

    def verify_buckets_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(LandingPage(self)._page_title_id, self._buckets_view_page_title)
        self.tester.wait_for_visible_by_id(LandingPage(self)._refresh_button_id)
