from selenium import webdriver
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.loginpage import LoginPage
from pages.keypair.keypairdetail import KeypairDetailPage
from selenium_api.selenium_api import SeleniumApi
from pages.keypair.keypairlanding import KeypairLandingPage
from dialogs.create_keypair_dialog import CreateKeypairDialog
from dialogs.delete_keypair_modal import DeleteKeypairModal

class GuiTester(SeleniumApi):

    def __init__(self, webdriver_url, console_url, account="ui-test-acct-00", user="admin", password="mypassword0"):
        """
        Initiates a  tester object. Initiates a copy of the browser. Opens console_url.
        :param webdriver_url:
        :param console_url:
        :param account:
        :param user:
        :param password:
        """
        self.driver = webdriver.Remote(webdriver_url, webdriver.DesiredCapabilities.FIREFOX)
        self.driver.implicitly_wait(60)
        self.driver.maximize_window()
        self.driver.get(console_url)
        self.account = account
        self.user = user
        self.password = password

    def set_implicit_wait(self, time_to_wait):
        """
        Sets implicit wait to time_to_wait
        :param time_to_wait:
        """
        self.driver.implicitly_wait(time_to_wait=time_to_wait)

    def login(self, account, username, password):
        """
        Logs in to eucaconsole with credentials specified in the GuiTester object, verifies dashboard is loaded.
        :param account:
        :param username:
        :param password:
        """
        LoginPage(self).login(account, username, password)
        Dashboard(self).verify_dashboard_loaded()

    def create_keypair_from_dashboard(self, keypair_name):
        """
        Goes to Dashboard, creates keypair.
        :param keypair_name:
        """
        pass

    def create_keypair_from_keypair_landing(self, keypair_name):
        """
        Goes from Dashboard to keypair landing page via menu. Creates keypair, verifies keypair detail page is loaded after keypair creation.
        """
        BasePage(self).goto_keypair_landing_via_menu()
        KeypairLandingPage(self).verify_keypair_landing_page_loaded()
        KeypairLandingPage(self).click_create_keypair_button_on_landing_page()
        CreateKeypairDialog(self).create_keypair(keypair_name)
        KeypairDetailPage(self).verify_keypair_detail_page_loaded()

    def import_keypair(self, keypair_name):
        pass

    def delete_keypair_from_detail_page(self, kekeypair_name):
        """
        Goes to keypair landing page, finds keypair, goes to keypair detail page via keypair name link. Deletes keypair.
        :param kekeypair_name:
        """
        BasePage(self).goto_keypair_landing_via_menu()
        KeypairLandingPage(self).verify_keypair_landing_page_loaded()
        KeypairLandingPage(self).click_keypair_link_on_landing_page(kekeypair_name)
        KeypairDetailPage(self).verify_keypair_detail_page_loaded()
        KeypairDetailPage(self).click_action_delete_keypair_on_detail_page()
        DeleteKeypairModal(self).click_delete_keypair_submit_button()
        BasePage(self).goto_keypair_landing_via_menu()
        KeypairLandingPage(self).verify_keypair_not_present_on_landing(kekeypair_name)

    def delete_keypair_from_landing_page(self, kekeypair_name):
        pass

    def goto_dashboard(self):
        Dashboard(self).goto_keypair_landing_via_hamburger()

    def exit_browser(self):
        """
        Closes browser.
        """
        self.driver.quit()

    def logout(self):
        """
        Logs out the user.
        """
        BasePage(self).logout()