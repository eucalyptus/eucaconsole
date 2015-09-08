from pages.landingpage import LandingPage


class EipLanding(LandingPage):
    def __init__(self, tester):
        self.tester = tester
        self.verify_eip_lp_loaded()

    def verify_eip_lp_loaded(self):
        pass
