import unittest
from guiops.tests.base import BaseTestCase
from guiops.pages.loginpage import LoginPage
from guiops.pages.basepage import BasePage
from guiops.pages.dashboard import Dashboard

class LoginTest(BaseTestCase):


    def test_euca_login(self):
        self.click_on_visible("XPATH", LoginPage._eucalyptus_log_in_tab_xpath)
        self.click_on_visible("ID", LoginPage._eucalyptus_account_field_id)
        self.send_keys_by_id(LoginPage._eucalyptus_account_field_id,BaseTestCase.account)
        self.send_keys_by_id(LoginPage._eucalyptus_username_field_id,BaseTestCase.user)
        self.send_keys_by_id(LoginPage._eucalyptus_password_field_id,BaseTestCase.password)
        self.click_on_visible("ID", LoginPage._eucalyptus_login_button_id)
        self.verify_visible_element_by_xpath(Dashboard._launch_instance_button_xpath)



    def test_euca_logout(self):
        self.click_on_visible("XPATH",BasePage._user_dropdown_xpath)
        self.click_on_visible("ID", BasePage._user_logout_id)



if __name__ == '__main__':
        unittest.main()


