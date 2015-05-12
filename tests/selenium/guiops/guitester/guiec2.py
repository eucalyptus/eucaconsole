from guitester import GuiTester
from selenium import webdriver
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.loginpage import LoginPage
from pages.keypair.keypairdetail import KeypairDetailPage
from selenium_api.selenium_api import SeleniumApi
from pages.keypair.keypairview import KeypairView
from dialogs.keypair_dialogs import CreateKeypairDialog


class GuiEC2(GuiTester):

    def __init__(self, webdriver_url, console_url, account="ui-test-acct-00", user="admin", password="mypassword0"):
        super(GuiEC2, self).__init__(webdriver_url, console_url, account=account, user=user, password=password)

    def create_keypair_from_landing(self, keypair_name):
        """
        Goes from Dashboard to keypair landing page via menu. Creates keypair, verifies keypair detail page is loaded after keypair creation.
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).verify_keypair_landing_page_loaded()
        KeypairView(self).click_create_keypair_button_on_landing_page(keypair_name)
        CreateKeypairDialog(self).create_keypair(keypair_name)
        KeypairDetailPage(self).verify_keypair_detail_page_loaded()




