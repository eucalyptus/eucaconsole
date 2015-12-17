from guiops.guiops import GuiOps
from option_parser import Option_parser


class RegionOperationsSequence(GuiOps):

    def __init__(self):
        parser = Option_parser()
        self.console_url = parser.parse_options()['console_url']
        self.webdriver_url = parser.parse_options()['web_driver']
        self.account = parser.parse_options()['account']
        self.user = parser.parse_options()['user_name']
        self.password = parser.parse_options()['password']
        self.sauce = parser.parse_options()['sauce']
        self.browser = parser.parse_options()['browser']
        self.version = parser.parse_options()['version']
        self.platform = parser.parse_options()['platform']
        self.tester = GuiOps(console_url=self.console_url, webdriver_url=self.webdriver_url,
                             sauce=self.sauce, browser=self.browser, version=self.version, platform=self.platform)

    def region_ops_test(self):
        self.tester.login(self.account, self.user, self.password)
        regions = self.tester.get_region_list()
        self.tester.change_region(regions[0])
        volume1_name = self.id_generator()+"-volume"
        volume1 = self.tester.create_volume_from_view_page(volume1_name, volume_size=1, availability_zone="one")
        volume1_id = volume1.get("volume_id")

        self.tester.change_region(regions[1])
        volume2 = self.tester.create_volume_from_dashboard(volume_size=1, availability_zone="two")
        volume2_id = volume2.get("volume_id")

        self.tester.change_region(regions[0])
        self.tester.delete_volume_from_view_page(volume1_id)

        self.tester.change_region(regions[1])
        self.tester.delete_volume_from_detail_page(volume2_id)
        self.tester.logout()
        self.tester.exit_browser()


if __name__ == '__main__':
        tester = RegionOperationsSequence()
        RegionOperationsSequence.region_ops_test(tester)
