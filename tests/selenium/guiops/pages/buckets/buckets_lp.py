from pages.landingpage import LandingPage


class BucketsLanding(LandingPage):

    def __init__(self, tester):
        super(BucketsLanding, self).__init__(tester)
        self.verify_buckets_view_page_loaded()

    _create_bucket_btn_id = 'create-bucket-btn'
    _buckets_view_page_title = 'Buckets'
    _bucket_link_css = 'td>a[href="/buckets/{0}/contents/"]'
    _bucket_actions_menu_id = 'table-item-dropdown_{0}'
    _view_contents_bucket_actions_menuitem_css ='#item-dropdown_{0}>li>a[href="/buckets/{0}/contents/"]'
    _view_details_bucket_actions_menuitem_css = '#item-dropdown_{0}>li>a[href="/buckets/{0}/details/"]'
    _delete_bucket_actions_menuitem_css = '#item-dropdown_{0}>li>a[ng-click="revealModal(\'delete-bucket\', item)"]'

    def verify_buckets_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(
            LandingPage(self)._page_title_id, self._buckets_view_page_title)
        self.tester.wait_for_visible_by_id(LandingPage(self)._refresh_button_id)

    def verify_bucket_not_present_on_landing_page(self, bucket_name):
        self.tester.wait_for_element_not_present_by_css(
            self._bucket_link_css.format(bucket_name))

    def click_create_bucket_on_view_page(self):
        self.tester.click_element_by_id(self._create_bucket_btn_id)

    def click_bucket_link_on_view_page(self, bucket_name):
        self.tester.click_element_by_css(self._bucket_link_css.format(bucket_name))

    def click_action_view_contents_on_view_page(self, bucket_name):
        self.tester.click_element_by_id(self._bucket_actions_menu_id.format(bucket_name))
        self.tester.click_element_by_css(
            self._view_contents_bucket_actions_menuitem_css.format(bucket_name))

    def click_action_view_details_on_view_page(self, bucket_name):
        self.tester.click_element_by_id(self._bucket_actions_menu_id.format(bucket_name))
        self.tester.click_element_by_css(
            self._view_details_bucket_actions_menuitem_css.format(bucket_name))

    def click_action_delete_bucket_on_view_page(self, bucket_name):
        self.tester.click_element_by_id(self._bucket_actions_menu_id.format(bucket_name))
        self.tester.click_element_by_css(
            self._delete_bucket_actions_menuitem_css.format(bucket_name))
