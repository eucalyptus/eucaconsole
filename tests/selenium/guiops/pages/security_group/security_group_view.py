from pages.viewpage import ViewPage

class SecurityGroupView(ViewPage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_keypair_landing_page_loaded()
