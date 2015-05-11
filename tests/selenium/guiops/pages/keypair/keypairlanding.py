from pages.landingpage import LandingPage
from dialogs.create_keypair_dialog import CreateKeypairDialog
from pages.keypair.keypairdetail import KeypairDetailPage

class KeypairLandingPage(LandingPage):

    def __init__(self, tester):
        self.tester = tester

    _keypair_landing_page_title = "Key Pairs"
    _create_keypair_btn_id = "create-keypair-btn"
    _import_keypair_btn_css = "#create-keypair-btn + a"

    def verify_keypair_landing_page_loaded(self):
        """
        Waits for page title to load; waits for refresh button to load; wait for 'Create New Key Pair' button to load.
        """
        self.tester.wait_for_text_present_by_id(LandingPage._page_title_id, self._keypair_landing_page_title)
        self.tester.wait_for_visible_by_id(LandingPage._refresh_button_id)
        self.tester.wait_for_visible_by_id(self._create_keypair_btn_id)

    def click_create_keypair_button_on_landing_page(self, keypair_name):
        self.tester.click_element_by_id(self._create_keypair_btn_id)

    def import_keypair_from_landing(self , keypair_name):
        self.tester.click_element_by_css(self._import_keypair_btn_css)
        CreateKeypairDialog(self).create_keypair(keypair_name)
        KeypairDetailPage(self).verify_keypair_detail_page_loaded()

    def verify_keypair_present_on_landing(self, keypair_name):
        pass

    def verify_keypair_not_present_on_landing(self, keypair_name):
        pass

    def delete_keypair_on_landing(self, keypair_name):
        pass

