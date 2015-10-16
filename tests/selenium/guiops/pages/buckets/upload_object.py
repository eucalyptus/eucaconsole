from pages.detailpage import BasePage


class UploadObjectPage(BasePage):

    def __init__(self, tester, bucket_name):
        super(UploadObjectPage, self).__init__(tester)
        self.bucket_name = bucket_name
        self.verify_upload_object_page_loaded()

    _upload_object_page_title = '{0}'

    def verify_upload_object_page_loaded(self):
        self.tester.wait_for_text_present_by_id(
            BasePage(self)._page_title_id,
            self._upload_object_page_title.format(self.bucket_name))
