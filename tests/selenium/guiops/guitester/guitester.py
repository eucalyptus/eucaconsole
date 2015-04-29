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

    def login(self):
        """
        Logs in to eucaconsole with credentials specified in the GuiTester object, verifies dashboard is loaded.
        """
        LoginPage(self).login()
        Dashboard(self).verify_dashboard_loaded()

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