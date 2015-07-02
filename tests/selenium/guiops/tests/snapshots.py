from guitester.guiec2 import GuiEC2
import string, random, time


class Snapshot_operations_sequence(GuiEC2):

    def __init__(self):
        self.tester = GuiEC2(console_url="https://10.111.5.145", webdriver_url="http://10.111.80.147:4444/wd/hub")

    def id_generator(self, size = 6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for j in range(size))

    def snapshot_ops_test(self):
        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        volume1_name = self.id_generator()+"-volume"
        volume1 = self.tester.create_volume_from_view_page(volume1_name, availability_zone="one")
        volume1_id = volume1.get("volume_id")
        snapshot1 = self.tester.create_snapshot_on_volumes_view_page(volume1_id, snapshot_description="Created by a GUI test")
        snapshot1_id = snapshot1.get("snapshot_id")
        snapshot2 = self.tester.create_snapshot_from_dashboard(volume1_id, "Oh-snap", "Created by GUI test")
        snapshot2_id = snapshot2.get("snapshot_id")
        snapshot3 = self.tester.create_snapshot_on_snapshot_view_page(volume1_id, "Dum-dum", "Created by GUI test")
        snapshot3_id = snapshot3.get("snapshot_id")
        snapshot4 = self.tester.create_snapshot_on_volumes_view_page(volume1_id)
        snapshot4_id = snapshot4.get("snapshot_id")
        self.tester.delete_snapshot_from_landing_page(snapshot4_id)
        self.tester.delete_snapshot_from_detail_page(snapshot1_id)
        self.tester.delete_snapshot_from_landing_page(snapshot2_id)
        self.tester.delete_snapshot_from_landing_page(snapshot3_id)
        self.tester.delete_volume_from_view_page(volume1_id)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Snapshot_operations_sequence()
        Snapshot_operations_sequence.snapshot_ops_test(tester)