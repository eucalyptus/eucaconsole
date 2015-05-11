from pages.landingpage import LandingPage
from guitester.guitester import GuiTester
from dialogs.create_keypair_dialog import CreateKeypairDialog

class KeypairLandingPage(LandingPage):

    def __init__(self, tester):
        assert isinstance(tester, GuiTester)
        self.tester = tester

    _create_keypair_btn_id = "create-keypair-btn"
    _import_keypair_btn_css = "#create-keypair-btn + a"

    def create_keypair_from_landing(self, keypair_name):
        self.click_element_by_id(self._create_keypair_btn_id)
        CreateKeypairDialog.create_keypair(keypair_name)

    def import_keypair_from_landing(self , keypair_name):
        self.click_element_by_css(self._import_keypair_btn_css)
        CreateKeypairDialog.create_keypair(keypair_name)

    def verify_keypair_present_on_landing(self, keypair_name):
        pass

    def verify_keypair_not_present_on_landing(self, keypair_name):
        pass

    def delete_keypair_on_landing(self, keypair_name):
        pass

