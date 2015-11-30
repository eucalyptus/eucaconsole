from pages.basepage import BasePage


class CreateBucketPage(BasePage):

    def __init__(self, tester):
        super(CreateBucketPage, self).__init__(tester)

    _page_title = "Create new bucket"
    _bucket_name_field_id = 'bucket_name'
    _create_bucket_id = 'create-bucket-submit-button'

    def verify_create_bucket_page_loaded(self):
        self.tester.wait_for_text_present_by_id(BasePage(self)._page_title_id, self._page_title)
        self.tester.wait_for_element_present_by_id(self._name_input_field_id)

    def create_bucket(self, bucket_name=None):
        if bucket_name is not None:
            self.tester.send_keys_by_id(self._bucket_name_field_id, bucket_name)
        self.tester.click_element_by_id(self._create_bucket_id)

