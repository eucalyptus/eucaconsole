from guiops.guiops import GuiOps
from option_parser import Option_parser

class SnapshotOperationsSequence(GuiOps):
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
        self.tester = GuiOps(console_url=self.console_url, webdriver_url=self.webdriver_url, sauce=self.sauce,
                             browser=self.browser, version=self.version, platform=self.platform)
        self.tester.zoom_out()

    def snapshot_ops_test(self):
        print ""
        print "Logging in ..."
        print ""
        self.tester.login(self.account, self.user, self.password)
        volume1_name = self.id_generator() + "-volume"
        print ""
        print "Creating volume"+volume1_name+"from view page ..."
        print ""
        volume1 = self.tester.create_volume_from_view_page(volume1_name, availability_zone=self.zone1)
        volume1_id = volume1.get("volume_id")
        print ""
        print "Creating snapshot without name on volume view page ..."
        print ""
        snapshot1 = self.tester.create_snapshot_on_volumes_view_page(
            volume1_id, snapshot_description="Created by snapshot operations test")
        snapshot1_id = snapshot1.get("snapshot_id")
        print ""
        print "Creates snapshot "+snapshot1_id
        print ""
        snapshot2_name = self.id_generator() + "-snapshot"
        print ""
        print "Running create_snapshot_from_dashboard with name "+snapshot2_name
        print ""
        snapshot2 = self.tester.create_snapshot_from_dashboard(
            volume1_id, snapshot2_name, "Created by snapshot operations test")
        snapshot2_id = snapshot2.get("snapshot_id")
        print ""
        print "Created snapshot named "+snapshot2_name+" id "+snapshot2_id
        print ""
        print ""
        print "Running launch_instance_from_dashboard..."
        print ""
        instance1 = self.tester.launch_instance_from_dashboard(availability_zone=self.zone1)
        instance1_id = instance1.get("instance_id")
        print ""
        print "Launched instance id "+instance1_id
        print ""
        print ""
        print "Running attach_volume_from_instance_lp "+volume1_id+" attaching to instance "+instance1_id
        print ""
        self.tester.attach_volume_from_instance_lp(volume1_id, instance1_id, device="/dev/vdg")
        snapshot3_name = self.id_generator() + "-snapshot"
        print ""
        print "Running create_snapshot_on_snapshot_view_page "+volume1_id+" snapshot by name "+snapshot3_name
        print ""
        snapshot3 = self.tester.create_snapshot_on_snapshot_view_page(
            volume1_id, snapshot3_name, "Created by snapshot operations test")
        snapshot3_id = snapshot3.get("snapshot_id")
        print ""
        print ""
        print ""
        print ""
        print ""
        print ""
        image1 = self.tester.register_snapshot_as_an_image_from_snapshot_landing_page(
            snapshot3_id, self.id_generator() + "-image")
        image1_id = image1.get("image_id")
        self.tester.remove_image_from_cloud_on_images_lp(image1_id)
        volume2 = self.tester.create_volume_from_snapshot_on_snapshot_lp(snapshot3_id, availability_zone=self.zone2)
        volume2_id = volume2.get("volume_id")
        self.tester.delete_volume_from_view_page(volume2_id)
        volume3_name = self.id_generator() + "-volume"
        volume3 = self.tester.create_volume_from_snapshot_on_snapshot_detail_page(
            snapshot3_id, volume_name=volume3_name, availability_zone=self.zone2)
        volume3_id = volume3.get("volume_id")
        self.tester.delete_volume_from_detail_page(volume3_id)
        snapshot4 = self.tester.create_snapshot_on_volumes_view_page(volume1_id)
        snapshot4_id = snapshot4.get("snapshot_id")
        image2 = self.tester.register_snapshot_as_an_image_from_snapshot_detail_page(
            snapshot4_id, self.id_generator() + "-image",
            description="Created by guitester automated snapshot test", register_as_windows_image=True)
        image2_id = image2.get("image_id")
        self.tester.remove_image_from_cloud_on_images_lp(image2_id, delete_associated_snapshot=True)
        self.tester.verify_snapshot_not_present_on_lp(snapshot4_id)
        self.tester.delete_snapshot_from_detail_page(snapshot1_id)
        self.tester.delete_snapshot_from_landing_page(snapshot2_id)
        self.tester.delete_snapshot_from_landing_page(snapshot3_id)
        self.tester.terminate_instance_from_view_page(instance1_id)
        self.tester.delete_volume_from_view_page(volume1_id)
        self.tester.logout()
        self.tester.exit_browser()


if __name__ == '__main__':
    tester = SnapshotOperationsSequence()
    SnapshotOperationsSequence.snapshot_ops_test(tester)
