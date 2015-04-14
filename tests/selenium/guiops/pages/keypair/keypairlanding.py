from pages.landingpage import LandingPage
from guitester.guitester import GuiTester

class KeypairLandingPage(LandingPage):

    def __init__(self, tester):
        assert isinstance(tester, GuiTester)
        self.tester = tester

    _create_keypair_btn_id = "create-keypair-btn"
    _import_keypair_btn_css = "#create-keypair-btn + a"


    def click_create_keypair_button(self):
        self.click_on_visible_by_id(self._create_keypair_btn_id)

    def click_import_keypair_button(self):
        self.click_on_visible_by_css_selector(self._import_keypair_btn_css)
