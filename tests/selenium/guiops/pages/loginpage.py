from basepage import BasePage


__author__ = 'alicehubenko'


class LoginPage(BasePage):
    _eucalyptus_log_in_tab_css = "#euca-tab>a"
    _eucalyptus_account_field_id = "account"
    _eucalyptus_username_field_id = "username"
    _eucalyptus_password_field_id = "password"
    _eucalyptus_login_button_id = "euca-login-button"
    _amazon_log_in_tab_css= "#aws-tab>a"

    def __init__(self, tester):
        self.tester = tester

    def login(self, account, username, password):
        self.tester.click_element_by_css(self._eucalyptus_log_in_tab_css)
        self.tester.send_keys_by_id(self._eucalyptus_account_field_id, account)
        self.tester.send_keys_by_id(self._eucalyptus_username_field_id, username)
        self.tester.send_keys_by_id(self._eucalyptus_password_field_id, password)
        self.tester.click_element_by_id(self._eucalyptus_login_button_id)




