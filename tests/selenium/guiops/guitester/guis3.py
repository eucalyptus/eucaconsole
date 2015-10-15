from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.buckets.buckets_lp import BucketsLanding
from pages.buckets.bucketdetail import BucketDetailPage
from pages.buckets.create_bucket import CreateBucketPage
from dialogs.bucket_dialogs import DeleteBucketModal
import logging


logger = logging.getLogger('testlogger')
hdlr = logging.FileHandler('/tmp/testlog.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.setLevel(logging.WARNING)


class GuiS3(GuiTester):

    def __init__(self, console_url, sauce=False, webdriver_url=None, browser=None, version=None, platform=None):
        super(GuiS3, self).__init__(console_url, webdriver_url=webdriver_url, sauce=sauce, browser=browser, version=version, platform=platform)

    def create_bucket_from_dashboard(self, bucket_name):
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_bucket_link()
        CreateBucketPage(self).create_bucket(bucket_name)
        BucketDetailPage(self, bucket_name)

    def create_bucket_from_landing_page(self, bucket_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_create_bucket_on_view_page()
        CreateBucketPage(self).create_bucket(bucket_name)
        BucketDetailPage(self, bucket_name)

    def view_contents_from_action_menu(self, bucket_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_action_view_contents_on_view_page(bucket_name)
        BucketDetailPage(self, bucket_name)

    def view_details_from_action_menu(self, bucket_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_action_view_details_on_view_page(bucket_name)
        BucketDetailPage(self, bucket_name)

    def delete_bucket_from_detail_page(self, bucket_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_bucket_link_on_view_page(bucket_name)
        BucketDetailPage(self).click_action_delete_bucket_on_detail_page(bucket_name)
        BucketDetailPage(self, bucket_name)

    def delete_bucket_from_view_page(self, bucket_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_action_delete_bucket_on_view_page(bucket_name)
        DeleteBucketModal(self).delete_bucket()
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).verify_bucket_not_present_on_landing_page(bucket_name)

