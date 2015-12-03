from guiops.guiops import GuiOps
from option_parser import Option_parser


class VolumeOperationsSequence(GuiOps):

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

    def volume_ops_test(self):
        self.tester.login(self.account, self.user, self.password)
        volume1_name = self.id_generator()+"-volume"
        volume1 = self.tester.create_volume_from_view_page(volume1_name, volume_size=2, availability_zone="one")
        volume1_id = volume1.get("volume_id")
        instance1 = self.tester.launch_instance_from_dashboard(availability_zone="one", timeout_in_seconds=400)
        instance1_id = instance1.get("instance_id")
        self.tester.attach_volume_from_instance_detail_page(volume1_id, instance1_id, timeout_in_seconds=400)
        self.tester.detach_volume_from_volumes_lp(volume1_id, timeout_in_seconds=800)
        self.tester.attach_volume_from_instance_lp(volume1_id, instance1_id, timeout_in_seconds=800)
        self.tester.detach_volume_from_volumes_lp(volume1_id, timeout_in_seconds=800)
        self.tester.attach_volume_from_volume_detail_page(instance1_id, volume1_id, device="/dev/vdd",
                                                          timeout_in_seconds=800)
        self.tester.detach_volume_from_volumes_lp(volume1_id, timeout_in_seconds=800)
        self.tester.attach_volume_from_volume_lp(instance1_id, volume1_id, timeout_in_seconds=800)
        self.tester.terminate_instance_from_view_page(instance1_id)
        self.tester.delete_volume_from_view_page(volume1_id)
        volume2 = self.tester.create_volume_from_dashboard(volume_size=3, availability_zone="two")
        volume2_id = volume2.get("volume_id")
        self.tester.delete_volume_from_detail_page(volume2_id)
        self.sortable_volumes_tables_test()
        self.tester.logout()
        self.tester.exit_browser()

    def sortable_volumes_tables_test(self):
        volume1_name = "!!!!"+self.id_generator()+"-volume"
        volume1 = self.tester.create_volume_from_view_page(volume1_name, volume_size=1, availability_zone="one")
        volume1_id = volume1.get("volume_id")
        volume2_name = "~~~~"+self.id_generator()+"-volume"
        volume2 = self.tester.create_volume_from_dashboard(volume2_name, volume_size=1, availability_zone="one")
        volume2_id = volume2.get("volume_id")
        # Test ascending sort by name column
        self.tester.click_sortable_column_header_on_volumes_landing_page(column_name='name')
        self.tester.verify_sort_position_for_volume(volume1_id, position=1)
        # Test descending sort by name column (second click sorts descending)
        self.tester.click_sortable_column_header_on_volumes_landing_page(column_name='name')
        self.tester.verify_sort_position_for_volume(volume2_id, position=1)
        # Cleanup volumes
        self.tester.delete_volume_from_view_page(volume1_id)
        self.tester.delete_volume_from_view_page(volume2_id)


if __name__ == '__main__':
        tester = VolumeOperationsSequence()
        VolumeOperationsSequence.volume_ops_test(tester)
