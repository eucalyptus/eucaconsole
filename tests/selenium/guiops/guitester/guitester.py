from selenium import webdriver
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.loginpage import LoginPage
from pages.keypair.keypairdetail import KeypairDetailPage
from selenium_api.selenium_api import SeleniumApi
from pages.keypair.keypairview import KeypairView
from dialogs.keypair_dialogs import CreateKeypairDialog, DeleteKeypairModal, ImportKeypairDialog

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
        Navigates to Dashboard via menu, creates keypair. Verifies keypair visible on Keypair View page.
        :param keypair_name:
        """
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_keypair_link_from_dashboard()
        CreateKeypairDialog(self).create_keypair(keypair_name)
        KeypairDetailPage(self).verify_keypair_detail_page_loaded()

    def create_keypair_from_keypair_landing(self, keypair_name):
        """
        Goes from Dashboard to keypair landing page via menu. Creates keypair, verifies keypair detail page is loaded after keypair creation.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).verify_keypair_landing_page_loaded()
        KeypairView(self).click_create_keypair_button_on_landing_page()
        CreateKeypairDialog(self).create_keypair(keypair_name)
        KeypairDetailPage(self).verify_keypair_detail_page_loaded()

    def import_keypair(self, keypair, keypair_name):
        """
        Navigates to Keypair View via menu. Imports keypair. Verifies keypair visible on Keypair View page.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).verify_keypair_landing_page_loaded()
        KeypairView(self).click_import_keypair_button()
        ImportKeypairDialog(self).import_keypair(keypair, keypair_name)
        KeypairDetailPage(self).verify_keypair_detail_page_loaded()

    def delete_keypair_from_detail_page(self, keypair_name):
        """
        Navigates to Keypair View via menu, finds keypair, goes to keypair detail page via keypair name link. Deletes keypair.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).verify_keypair_landing_page_loaded()
        KeypairView(self).click_keypair_link_on_view_page(keypair_name)
        KeypairDetailPage(self).verify_keypair_detail_page_loaded()
        KeypairDetailPage(self).click_action_delete_keypair_on_detail_page()
        DeleteKeypairModal(self).click_delete_keypair_submit_button()
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).verify_keypair_not_present_on_landing(keypair_name)

    def delete_keypair_from_view_page(self, keypair_name):
        """
        Navigates to Keypair View via menu. Deletes keypair from view page. Verifies keypair was removed from view page.
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).verify_keypair_landing_page_loaded()
        KeypairView(self).click_action_delete_keypair_on_landing(keypair_name)
        DeleteKeypairModal(self).click_delete_keypair_submit_button()
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).verify_keypair_not_present_on_landing(keypair_name)


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