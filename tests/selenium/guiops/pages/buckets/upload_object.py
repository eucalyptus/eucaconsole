from pages.detailpage import BasePage


class UploadObjectPage(BasePage):

    def __init__(self, tester, bucket_name):
        super(UploadObjectPage, self).__init__(tester)
        self.bucket_name = bucket_name
        self.verify_upload_object_page_loaded()

    _upload_object_page_title = 'Upload object(s)'
    _upload_object_bucket_path_selector = '#upload-file-form .bucket-path'
    _upload_object_submit_button_id = 'create-bucket-submit-button'
    _advanced_settings_toggle_selector = '#advance-section .title a'

    def verify_upload_object_page_loaded(self):
        self.tester.driver.switch_to.window('upload-file')
        self.tester.wait_for_text_present_by_id(
            BasePage(self)._page_title_id, self._upload_object_page_title)

    def expand_advanced_settings(self):
        self.tester.click_element_by_css(
            self._advanced_settings_toggle_selector)

    def upload_object_by_path(self, path):
        self.tester.send_keys_by_id('files', path, clear_field=False)
        self.tester.click_element_by_id(self._upload_object_submit_button_id)
