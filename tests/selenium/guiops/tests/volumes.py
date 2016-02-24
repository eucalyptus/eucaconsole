from guiops.guiops import GuiOps
from option_parser import Option_parser


class VolumeOperationsSequence(GuiOps):

    def __init__(self):
        parser = Option_parser()
        options = parser.parse_options()
        self.console_url = options['console_url']
        self.webdriver_url = options['web_driver']
        self.account = options['account']
        self.user = options['user_name']
        self.password = options['password']
        self.sauce = options['sauce']
        self.browser = options['browser']
        self.version = options['version']
        self.platform = options['platform']
        self.zones = self.get_zones_from_options(options)
        self.zone1 = self.zones.get(0)
        self.zone2 = self.zones.get(1, self.zones.get(0))
        self.tester = GuiOps(console_url=self.console_url, webdriver_url=self.webdriver_url,
                             sauce=self.sauce, browser=self.browser, version=self.version, platform=self.platform)

    def volume_ops_test(self):
        self.tester.login(self.account, self.user, self.password)
        volume1_name = self.id_generator()+"-volume"
        volume1 = self.tester.create_volume_from_view_page(volume1_name, volume_size=2, availability_zone=self.zone1)
        volume1_id = volume1.get("volume_id")
        instance1 = self.tester.launch_instance_from_dashboard(availability_zone=self.zone1, timeout_in_seconds=400)
        instance1_id = instance1.get("instance_id")
        self.tester.verify_attach_notice_on_volume_monitoring_page(volume1_id)
        self.tester.attach_volume_from_instance_detail_page(volume1_id, instance1_id, timeout_in_seconds=400)
        self.tester.verify_charts_on_volume_monitoring_page(volume1_id)
        self.tester.detach_volume_from_volumes_lp(volume1_id, timeout_in_seconds=800)
        self.tester.attach_volume_from_instance_lp(volume1_id, instance1_id, timeout_in_seconds=800)
        self.tester.detach_volume_from_volumes_lp(volume1_id, timeout_in_seconds=800)
        self.tester.attach_volume_from_volume_detail_page(instance1_id, volume1_id, device="/dev/vdd",
                                                          timeout_in_seconds=800)
        self.tester.detach_volume_from_volumes_lp(volume1_id, timeout_in_seconds=800)
        self.tester.attach_volume_from_volume_lp(instance1_id, volume1_id, timeout_in_seconds=800)
        self.tester.terminate_instance_from_view_page(instance1_id)
        self.tester.delete_volume_from_view_page(volume1_id)
        volume2 = self.tester.create_volume_from_dashboard(volume_size=3, availability_zone=self.zone2)
        volume2_id = volume2.get("volume_id")
        self.tester.delete_volume_from_detail_page(volume2_id)
        self.sortable_volumes_tables_test()
        self.tester.logout()
        self.tester.exit_browser()

    def sortable_volumes_tables_test(self):
        volume1_name = "!!!!"+self.id_generator()+"-volume"
        volume1 = self.tester.create_volume_from_view_page(volume1_name, volume_size=1, availability_zone=self.zone1)
        volume1_id = volume1.get("volume_id")
        volume2_name = "~~~~"+self.id_generator()+"-volume"
        volume2 = self.tester.create_volume_from_dashboard(volume2_name, volume_size=1, availability_zone=self.zone1)
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
