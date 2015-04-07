from selenium import webdriver
from guiops.guitester.guiec2 import GuiEC2
from guiops.pages.basepage import BasePage
from guiops.pages.dashboard import Dashboard
from guiops.pages.loginpage import LoginPage
from guiops.utilities import Utilities


class GuiTester(Utilities):
    def __init__(self, webdriver_url, console_url, account= "ui-test-acct-00", user= "admin", password= "mypassword0"):
        self.driver = webdriver.Remote(webdriver_url, webdriver.DesiredCapabilities.FIREFOX)
        self.driver.implicitly_wait(60)
        self.driver.maximize_window()
        self.driver.get(console_url)
        self.account=account
        self.user=user
        self.password=password

    def set_implicit_wait(self,time_to_wait):
        self.driver.implicitly_wait(time_to_wait=time_to_wait)

    def login(self):
        LoginPage(self).login()
        Dashboard(self).verify_dashboard_loaded()

    def exit_browser(self):
        self.driver.quit()

    def logout(self):
        BasePage(self).logout()


class GuiOps(GuiTester, GuiEC2):

    def set_all_views_to_table(self):
        pass

    def set_all_views_to_tile(self):
        pass