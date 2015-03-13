from guiops.utilities import Utilities
from guiops.pages.basepage import BasePage

__author__ = 'alicehubenko'


class LoginPage (BasePage):


        def __init__(self, driver):
            super(LoginPage, self).__init__(driver)
            self.driver=driver

        _eucalyptus_log_in_tab_xpath = "//dd[@id='euca-tab']/a"
        _eucalyptus_account_field_id = "account"
        _eucalyptus_username_field_id = "username"
        _eucalyptus_password_field_id = "password"
        _eucalyptus_login_button_id = "euca-login-button"
        _amazon_log_in_tab_xpath= "//dd[@id='aws-tab']/a"

