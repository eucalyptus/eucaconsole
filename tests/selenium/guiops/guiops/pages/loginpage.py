from guiops.pages.basepage import BasePage
from guiops.pages.dashboard import Dashboard
__author__ = 'alicehubenko'


class LoginPage(BasePage):
    _eucalyptus_log_in_tab_xpath = "//dd[@id='euca-tab']/a"
    _eucalyptus_account_field_id = "account"
    _eucalyptus_username_field_id = "username"
    _eucalyptus_password_field_id = "password"
    _eucalyptus_login_button_id = "euca-login-button"
    _amazon_log_in_tab_xpath= "//dd[@id='aws-tab']/a"

    def __init__(self, tester):
        self.tester=tester

    def login(self):
        self.tester.click_on_visible("XPATH", LoginPage._eucalyptus_log_in_tab_xpath)
        self.tester.click_on_visible("ID", LoginPage._eucalyptus_account_field_id)
        self.tester.send_keys_by_id(LoginPage._eucalyptus_account_field_id,self.tester.account)
        self.tester.send_keys_by_id(LoginPage._eucalyptus_username_field_id,self.tester.user)
        self.tester.send_keys_by_id(LoginPage._eucalyptus_password_field_id,self.tester.password)
        self.tester.click_on_visible("ID", LoginPage._eucalyptus_login_button_id)
        self.tester.verify_visible_element_by_xpath(Dashboard._launch_instance_button_xpath)



