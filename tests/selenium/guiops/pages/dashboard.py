from basepage import BasePage

class Dashboard(BasePage):

        _launch_instance_button_css='#item-dropdown_instances-running+div+div>a'
        _keypairs_icon_css='#key-pairs > div.tile > div.content > a > i.icon'
        _create_keypair_link_css='#item-dropdown_key-pairs+div+div>a'

        def __init__(self, tester):
            """
            :type tester: GuiTester
            :param tester:
            """
            self.tester = tester

        def verify_dashboard_loaded(self):
            self.tester.wait_for_visible_by_css_selector(self._launch_instance_button_css)

        def from_dashboard_goto_keypairs_lp_via_icon(self):
            self.tester.click_on_visible_by_css_selector(self._keypairs_icon_css)

        def click_create_keypair_link_from_dashboard(self):
            """
            Clicks create keypair link on Dashboard.
            """
            self.tester.click_on_visible_by_css_selector(Dashboard._create_keypair_link_css)

        def dashboard_click_keypair_tile(self,_keypairs_icon_css):
            """
            Clciks keypais tile on Dashboard.
            """
            self.tester.click_on_visible_by_css_selector(_keypairs_icon_css)






