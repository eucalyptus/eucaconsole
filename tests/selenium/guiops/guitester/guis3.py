from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.buckets.bucketdetail import BucketDetailPage
from dialogs.bucket_dialogs import CreateBucketDialog


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
        CreateBucketDialog.create_bucket(bucket_name)
        BucketDetailPage(self, bucket_name)

    def create_bucket_from_landing_page(self):
        pass

    def bucket_verify_landing_page(self):
        pass

    def view_contents_from_action_menu(self):
        pass

    def view_details_from_action_menu(self):
        pass
