from guiops.pages.basepage import BasePage
from guiops.tests.base import BaseTestCase


class Dashboard (BasePage):

        _launch_instance_button_xpath='//div[@id="running"]/div[2]/a'

        _keypairs_icon_xpath='//ul[@id="item-dropdown_key-pairs"]/../div/a/'
        _create_keypair_link_xpath='//ul[@id="item-dropdown_key-pairs"]/../div[2]/a'



class DashboardTests(BaseTestCase):

        def test_verify_dashnoard_loaded(self):
            self.wait_for_visible("XPATH",Dashboard._launch_instance_button_xpath)

        def test_from_dashboard_goto_keypairs_lp_via_icon(self):
            self.click_on_visible("XPATH", Dashboard._keypairs_icon_xpath)

        def test_call_create_keypair_dialog_from_dashboard(self):
            self.click_on_visible("XPATH",Dashboard._create_keypair_link_xpath)




