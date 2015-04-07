import unittest
from guiops.utilities import Utilities
from guiops.pages.dashboard import Dashboard

class DashboardTests(Utilities):


        def test_verify_dashboard_loaded(self):
            self.wait_for_visible("XPATH",Dashboard._launch_instance_button_xpath)

        def test_from_dashboard_goto_keypairs_lp_via_icon(self):
            self.click_on_visible("XPATH", Dashboard._keypairs_icon_xpath)

        def test_call_create_keypair_dialog_from_dashboard(self):
            self.click_on_visible("XPATH",Dashboard._create_keypair_link_xpath)


if __name__ == '__main__':
        unittest.main()