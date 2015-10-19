from pages.detailpage import BasePage


class BucketContentsPage(BasePage):

    def __init__(self, tester, bucket_name, switch=False):
        super(BucketContentsPage, self).__init__(tester)
        self.bucket_name = bucket_name
        if switch:
            self.tester.driver.switch_to.default_content()
        self.verify_bucket_contents_page()

    _bucket_contents_page_title_id = 'pagetitle'

    def verify_bucket_contents_page(self):
        pass

    def verify_object_in_bucket(self, object_name):
        self.tester.wait_for_element_present_by_link_text(object_name)
