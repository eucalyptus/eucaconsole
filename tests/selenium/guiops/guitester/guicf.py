from guitester import GuiTester
from pages.basepage import BasePage
from pages.loginpage import LoginPage
from pages.dashboard import Dashboard
from dialogs.stack_dialogs import DeleteStackDialog
from pages.stacks.create_stack import CreateStackWizard
from pages.stacks.stacks_lp import StacksLandingPage

class GuiCF(GuiTester):

    def __init__(self, console_url, sauce=False, webdriver_url=None, browser=None, version=None, platform=None):
        super(GuiCF, self).__init__(console_url, webdriver_url=webdriver_url, sauce=sauce, browser=browser, version=version, platform=platform)

    def login(self, account, username, password):
        """
        Logs in to eucaconsole with credentials specified in the GuiTester object, verifies dashboard is loaded.
        :param account:
        :param username:
        :param password:
        """
        LoginPage(self).login(account, username, password)
        Dashboard(self).verify_dashboard_loaded()

    def create_stack_from_dashboard(self, name):
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_stack_link()
        CreateStackWizard(self).create_stack(name)

    def delete_stack_from_dashboard(self, name):
        BasePage(self).goto_dashboard_via_menu()
        BasePage(self).goto_stacks_view_via_menu()
        StacksLandingPage(self).click_action_delete_stack_on_landing_page(name)
        DeleteStackDialog(self).delete_stack()
