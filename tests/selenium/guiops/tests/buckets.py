from guiops.guiops import GuiOps
from option_parser import Option_parser
import logging


class Buckets_operations_sequence(GuiOps):

    def __init__(self):
        parser = Option_parser()
        self.console_url = parser.parse_options()['console_url']
        self.webdriver_url = parser.parse_options()['web_driver']
        self.account = parser.parse_options()['account']
        self.user = parser.parse_options()['user_name']
        self.password = parser.parse_options()['password']
        self.sauce = parser.parse_options()['sauce']
        self.browser = parser.parse_options()['browser']
        self.version = parser.parse_options()['version']
        self.platform = parser.parse_options()['platform']

        self.tester = GuiOps(
            console_url=self.console_url,
            webdriver_url=self.webdriver_url,
            sauce=self.sauce,
            browser=self.browser,
            version=self.version,
            platform=self.platform)
        logging.basicConfig(format='%(asctime)s %(message)s')

    def get_bucket_name(self):
        return self.id_generator() + '-bucket'

    def bucket_ops_test(self):
        self.tester.login(self.account, self.user, self.password)

        self._create_from_dashboard()
        self._create_from_landing_page()
        self._upload_object_detail_page()
        self._upload_object_contents_page()
        self._delete_all_objects_from_contents_page()

        self.tester.logout()
        self.tester.exit_browser()

    def _create_from_dashboard(self):
        bucket_name = self.get_bucket_name()
        self.tester.create_bucket_from_dashboard(bucket_name)
        self.tester.delete_bucket_from_view_page(bucket_name)

    def _create_from_landing_page(self):
        bucket_name = self.get_bucket_name()
        self.tester.create_bucket_from_landing_page(bucket_name)
        self.tester.delete_bucket_from_detail_page(bucket_name)

    def _upload_object_detail_page(self):
        bucket_name = self.get_bucket_name()
        self.tester.create_bucket_from_landing_page(bucket_name)
        object_name = self.tester.upload_object_from_details_page(bucket_name)
        self.tester.delete_object_from_contents_page(bucket_name, object_name)
        self.tester.delete_bucket_from_detail_page(bucket_name)

    def _upload_object_contents_page(self):
        bucket_name = self.get_bucket_name()
        self.tester.create_bucket_from_landing_page(bucket_name)
        object_name = self.tester.upload_object_from_contents_page(bucket_name)
        self.tester.delete_object_from_contents_page(bucket_name, object_name)
        self.tester.delete_bucket_from_detail_page(bucket_name)

    def _delete_all_objects_from_contents_page(self):
        bucket_name = self.get_bucket_name()
        self.tester.create_bucket_from_landing_page(bucket_name)
        for _ in xrange(3):
            self.tester.upload_object_from_contents_page(bucket_name)
        self.tester.delete_all_objects_from_contents_page(bucket_name)
        self.tester.delete_bucket_from_detail_page(bucket_name)


if __name__ == '__main__':
    tester = Buckets_operations_sequence()
    tester.bucket_ops_test()
