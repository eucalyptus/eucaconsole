import unittest
from selenium_api.selenium_api import SeleniumApi
from pages.dashboard import Dashboard

class DashboardTests(SeleniumApi):


        def test_verify_dashboard_loaded(self):
            self.wait_for_visible("XPATH", Dashboard._launch_instance_button_css)

        def test_from_dashboard_goto_keypairs_lp_via_icon(self):
            self.click_on_visible("XPATH", Dashboard._keypairs_icon_css)

        def test_click_create_keypair_link_from_dashboard(self):
            """
            Clicks Create Keypair button on Dashboard.

            """
            self.click_on_visible("XPATH", Dashboard._create_keypair_link_css)


if __name__ == '__main__':
       DashboardTests()