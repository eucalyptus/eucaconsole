from guitester.guitester import GuiTester
from pages.landingpage import LandingPage
from pages.basepage import BasePage

class CreateKeypairDialog(LandingPage):

    _keypair_name_field_id="key-name"
    _create_and_download_button_css="button.button"

    def __init__(self, tester):
            assert isinstance(tester, GuiTester)
            self.tester = tester

    def create_keypair(self,keypair_name):
        self.tester.send_keys_by_css_selector(self._keypair_name_field_id, keypair_name)
        self.tester.click_on_visible_by_css_selector(self._create_and_download_button_css)


