import os.path
import logging
import tempfile

from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.buckets.buckets_lp import BucketsLanding
from pages.buckets.bucketdetail import BucketDetailPage
from pages.buckets.bucket_contents import BucketContentsPage
from pages.buckets.upload_object import UploadObjectPage
from pages.buckets.create_bucket import CreateBucketPage
from pages.buckets.bucket_dialogs import DeleteBucketModal
from pages.buckets.bucket_dialogs import DeleteObjectModal
from pages.buckets.bucket_dialogs import DeleteEverythingModal


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
        BucketsLanding(self).click_action_view_details_on_view_page(bucket_name)
        BucketDetailPage(self, bucket_name).click_action_delete_bucket_on_detail_page()
        DeleteBucketModal(self).delete_bucket()
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).verify_bucket_not_present_on_landing_page(bucket_name)

    def delete_bucket_from_view_page(self, bucket_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_action_delete_bucket_on_view_page(bucket_name)
        DeleteBucketModal(self).delete_bucket()
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).verify_bucket_not_present_on_landing_page(bucket_name)

    def upload_object_from_details_page(self, bucket_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_action_view_details_on_view_page(bucket_name)
        BucketDetailPage(self, bucket_name).click_action_upload_files_on_detail_page()

        upload_page = UploadObjectPage(self, bucket_name)
        with tempfile.NamedTemporaryFile('w') as local_object:
            local_object.write('This is a test file.')
            path = local_object.name
            object_name = os.path.basename(path)
            upload_page.upload_object_by_path(path)

        BucketDetailPage(self, bucket_name).click_action_view_contents_on_detail_page()
        BucketContentsPage(self, bucket_name).verify_object_in_bucket(object_name)

        return object_name

    def upload_object_from_contents_page(self, bucket_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_action_view_contents_on_view_page(bucket_name)
        BucketContentsPage(self, bucket_name).click_upload_object_button()

        upload_page = UploadObjectPage(self, bucket_name)
        with tempfile.NamedTemporaryFile('w') as local_object:
            local_object.write('This is a test file.')
            path = local_object.name
            object_name = os.path.basename(path)
            upload_page.upload_object_by_path(path)

        BucketContentsPage(self, bucket_name).verify_object_in_bucket(object_name)

        return object_name

    def delete_object_from_contents_page(self, bucket_name, object_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_action_view_contents_on_view_page(bucket_name)
        BucketContentsPage(self, bucket_name).click_action_delete_object_in_bucket(object_name)
        DeleteObjectModal(self).delete_object()

    def delete_all_objects_from_contents_page(self, bucket_name):
        BasePage(self).goto_buckets_view_via_menu()
        BucketsLanding(self).click_action_view_contents_on_view_page(bucket_name)
        BucketContentsPage(self, bucket_name).delete_all_objects_in_bucket()
        DeleteEverythingModal(self).delete_all()
