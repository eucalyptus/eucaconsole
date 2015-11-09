from guitester import GuiTester
from pages.basepage import BasePage
from pages.loginpage import LoginPage
from pages.dashboard import Dashboard
from dialogs.stack_dialogs import DeleteStackDialog
from pages.stacks.create_stack import CreateStackWizard
from pages.stacks.stacks_lp import StacksLandingPage
from pages.stacks.stacksdetail import StackDetailPage

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

    def create_stack_from_dashboard(self, name, template_url=None):
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_stack_link()
        CreateStackWizard(self).create_stack(name, template_url)

    def create_stack_from_lp(self, name):
        BasePage(self).goto_stacks_view_via_menu()
        StacksLandingPage(self).click_create_stack_button_on_landing_page()
        CreateStackWizard(self).create_stack(name)

    def delete_stack_from_lp(self, name):
        BasePage(self).goto_stacks_view_via_menu()
        StacksLandingPage(self).click_action_delete_stack_on_landing_page(name)
        DeleteStackDialog(self).delete_stack()

    def delete_stack_from_detail_page(self, name):
        BasePage(self).goto_stacks_view_via_menu()
        StacksLandingPage(self).click_action_view_stack_details_on_landing_page(name)
        StackDetailPage(self, name).verify_stack_detail_page_loaded()
        StackDetailPage(self, name).click_action_delete_stack_on_detail_page()
        DeleteStackDialog(self).delete_stack()
