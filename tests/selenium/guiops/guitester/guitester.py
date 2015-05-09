from selenium import webdriver
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.loginpage import LoginPage
from selenium_api.selenium_api import SeleniumApi


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
        pass

    def import_keypair(self, keypair_name):
        pass

    def delete_keypair_from_detail_page(self, kekeypair_name):
        pass

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