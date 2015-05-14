from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.loginpage import LoginPage
from pages.keypair.keypairdetail import KeypairDetailPage
from pages.keypair.keypairview import KeypairView
from pages.security_group.security_group_view import SecurityGroupView
from pages.security_group.security_group_detail import SecurityGroupDetailPage
from dialogs.security_group_dialogs import CreateScurityGroupDialog
from dialogs.keypair_dialogs import CreateKeypairDialog, DeleteKeypairModal, ImportKeypairDialog



class GuiEC2(GuiTester):

    def __init__(self, webdriver_url, console_url, account="ui-test-acct-00", user="admin", password="mypassword0"):
        super(GuiEC2, self).__init__(webdriver_url, console_url, account=account, user=user, password=password)

    def set_implicit_wait(self, time_to_wait):
        """
        Sets implicit wait to time_to_wait
        :param time_to_wait:
        """
        self.driver.implicitly_wait(time_to_wait)

    def login(self, account, username, password):
        """
        Logs in to eucaconsole with credentials specified in the GuiTester object, verifies dashboard is loaded.
        :param account:
        :param username:
        :param password:
        """
        LoginPage(self).login(account, username, password)
        Dashboard(self).verify_dashboard_loaded()

    def set_all_pages_to_list_view(self):
        pass

    def set_all_pages_to_tile_view(self):
        pass

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

    def create_keypair_from_dashboard(self, keypair_name):
        """
        Navigates to Dashboard via menu, creates keypair. Verifies keypair visible on Keypair View page.
        :param keypair_name:
        """
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_keypair_link_from_dashboard()
        CreateKeypairDialog(self).create_keypair(keypair_name)
        KeypairDetailPage(self, keypair_name)

    def create_keypair_from_keypair_view_page(self, keypair_name):
        """
        Goes from Dashboard to keypair landing page via menu. Creates keypair, verifies keypair detail page is loaded after keypair creation.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).click_create_keypair_button_on_view_page()
        CreateKeypairDialog(self).create_keypair(keypair_name)
        KeypairDetailPage(self, keypair_name)

    def import_keypair(self, keypair, keypair_name):
        """
        Navigates to Keypair View via menu. Imports keypair. Verifies keypair visible on Keypair View page.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).click_import_keypair_button()
        ImportKeypairDialog(self).import_keypair(keypair, keypair_name)
        KeypairDetailPage(self, keypair_name)

    def delete_keypair_from_detail_page(self, keypair_name):
        """
        Navigates to Keypair View via menu, finds keypair, goes to keypair detail page via keypair name link. Deletes keypair.
        :param keypair_name:
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).click_keypair_link_on_view_page(keypair_name)
        KeypairDetailPage(self, keypair_name).click_action_delete_keypair_on_detail_page()
        DeleteKeypairModal(self).click_delete_keypair_submit_button()
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).verify_keypair_not_present_on_view_page(keypair_name)

    def delete_keypair_from_view_page(self, keypair_name):
        """
        Navigates to Keypair View via menu. Deletes keypair from view page. Verifies keypair was removed from view page.
        """
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).click_action_delete_keypair_on_view_page(keypair_name)
        DeleteKeypairModal(self).click_delete_keypair_submit_button()
        BasePage(self).goto_keypair_view_page_via_menu()
        KeypairView(self).verify_keypair_not_present_on_view_page(keypair_name)

    def create_security_group_from_dashboard(self, s_group_name, s_group_description):
        """
        Creates security group from dashboard without adding rules or tags.
        """
        BasePage(self).goto_dashboard_via_menu()
        Dashboard(self).click_create_s_group_link_from_dashboard()
        CreateScurityGroupDialog(self).create_s_group(s_group_name, s_group_description)
        SecurityGroupDetailPage(self, s_group_name)

    def create_security_group_from_view_page(self, sgroup_name):
        """
        Creates security group from S. groups view page without adding rules or tags.
        """
        pass

    def edit_security_group(self, sgroup_name):
        pass

    def delete_security_group_from_view_page(self, sgroup_name):
        pass

    def delete_security_group_from_detail_page(self, sgroup_name):
        pass





