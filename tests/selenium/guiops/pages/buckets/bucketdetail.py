from pages.detailpage import DetailPage


class BucketDetailPage(DetailPage):

    def __init__(self, tester, bucket_name):
        self.bucket_name = bucket_name
        self.tester = tester
        self.verify_bucket_detail_page_loaded()

    _bucket_detail_page_title = "Details for bucket: {0}"
    _delete_bucket_action_menuitem_id = "delete-bucket-action"

    def verify_bucket_detail_page_loaded(self):
        self.tester.wait_for_text_present_by_id(
            DetailPage._detail_page_title_id,
            self._bucket_detail_page_title.format(self.bucket_name))

    def click_action_delete_bucket_on_detail_page(self):
        self.tester.click_element_by_css(self._actions_menu_css)
        self.tester.click_element_by_id(self._delete_bucket_action_menuitem_id)
