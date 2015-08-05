from guiops.guiops import GuiOps
from option_parser import Option_parser
import string, random, time


class Volume_operations_sequence(GuiOps):

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
        self.tester = GuiOps(console_url=self.console_url, webdriver_url=self.webdriver_url, sauce=self.sauce, browser=self.browser, version=self.version, platform=self.platform)

    def id_generator(self, size = 6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for j in range(size))

    def volume_ops_test(self):
        self.tester.login(self.account, self.user, self.password)
        volume1_name = self.id_generator()+"-volume"
        volume1 = self.tester.create_volume_from_view_page(volume1_name, volume_size=2, availability_zone="one")
        volume1_id = volume1.get("volume_id")
        instance1=self.tester.launch_instance_from_dashboard(availability_zone="one", timeout_in_seconds=400)
        instance1_id=instance1.get("instance_id")
        self.tester.attach_volume_from_instance_detail_page(volume1_id, instance1_id,timeout_in_seconds=400)
        self.tester.detach_volume_from_volumes_lp(volume1_id,timeout_in_seconds=400)
        self.tester.attach_volume_from_instance_lp(volume1_id, instance1_id,timeout_in_seconds=400)
        self.tester.detach_volume_from_volumes_lp(volume1_id, timeout_in_seconds=400)
        self.tester.attach_volume_from_volume_detail_page(instance1_id, volume1_id, device="/dev/vdd", timeout_in_seconds=400)
        self.tester.detach_volume_from_volumes_lp(volume1_id, timeout_in_seconds=400)
        self.tester.attach_volume_from_volume_lp(instance1_id, volume1_id, timeout_in_seconds=400)
        self.tester.terminate_instance_from_view_page(instance1_id)
        self.tester.delete_volume_from_view_page(volume1_id)
        volume2=self.tester.create_volume_from_dashboard(volume_size=3, availability_zone="two")
        volume2_id=volume2.get("volume_id")
        self.tester.delete_volume_from_detail_page(volume2_id)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Volume_operations_sequence()
        Volume_operations_sequence.volume_ops_test(tester)