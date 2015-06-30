from selenium import webdriver
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.loginpage import LoginPage
from pages.keypair.keypairdetail import KeypairDetailPage
from selenium_api.selenium_api import SeleniumApi
from pages.keypair.keypairview import KeypairView
from dialogs.keypair_dialogs import CreateKeypairDialog, DeleteKeypairModal, ImportKeypairDialog

class GuiTester(SeleniumApi):

    def __init__(self, console_url, webdriver_url=None, account="ui-test-acct-00", user="admin", password="mypassword0"):
        """
        Initiates a  tester object. Initiates a copy of the browser. Opens console_url.
        :param webdriver_url:
        :param console_url:
        :param account:
        :param user:
        :param password:
        """

        ffprofile = webdriver.FirefoxProfile()
        ffprofile.set_preference("browser.download.folderList",2)
        ffprofile.set_preference("browser.download.manager.showWhenStarting", False)
        ffprofile.set_preference("browser.download.dir", "/tmp/")
        ffprofile.set_preference("browser.helperApps.alwaysAsk.force", False)
        ffprofile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-pem-file, text/csv, application/xml, text/plain, image/jpeg, application/x-apple-diskimage, application/zip")
        ffprofile.update_preferences()

        if webdriver_url is None:
            self.driver = webdriver.Firefox(firefox_profile=ffprofile)
            print "Using local webdriver"
        else:
            self.driver = webdriver.Remote(webdriver_url, webdriver.DesiredCapabilities.FIREFOX, browser_profile=ffprofile)
            print "Using remote webdriver " + webdriver_url
        print "Setting webdriver profile"
        self.driver.implicitly_wait(60)
        self.driver.maximize_window()
        self.driver.get(console_url)
        self.account = account
        self.user = user
        self.password = password

