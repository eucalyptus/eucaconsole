from basepage import BasePage
from string import split

class Dashboard(BasePage):

        _launch_instance_button_css ='#item-dropdown_instances-running+div+div>a'
        _keypairs_icon_css ='#key-pairs > div.tile > div.content > a > i.icon'
        _create_keypair_link_css ='#item-dropdown_key-pairs+div+div>a'
        _create_volume_link_css = 'a[href="/volumes/new"]'
        _create_snapshot_link_css = 'a[href="/snapshots/new"]'
        _availability_zone_menu_css = "#zone-selector>a"
        _availability_zone_dropdown_id = "zone-dropdown"
        _first_availability_zone_on_list_css = "ul#zone-dropdown>li:nth-of-type(2)>a"
        _create_s_group_link_css = 'a[href="/securitygroups/new"]'


        def __init__(self, tester):
            """
            :type tester: GuiTester
            :param tester:
            """
            self.tester = tester

        def verify_dashboard_loaded(self):
            """
            Waits for the 'Launch instance' button to become visible
            """
            self.tester.wait_for_visible_by_css(self._launch_instance_button_css)

        def click_create_keypair_link_from_dashboard(self):
            """
            Clicks create keypair link on Dashboard.
            """
            self.tester.click_element_by_css(Dashboard._create_keypair_link_css)

        def click_create_volume_link(self):
            self.tester.click_element_by_css(self._create_volume_link_css)

        def click_create_snapshot_link(self):
            self.tester.click_element_by_css(self._create_snapshot_link_css)

        def dashboard_click_keypair_tile(self, _keypairs_icon_css):
            """
            Clciks keypais tile on Dashboard.
            """
            self.tester.click_element_by_css(_keypairs_icon_css)

        def click_create_s_group_link_from_dashboard(self):
            """
            Clicks create security group link on Dashboard.
            """
            self.tester.click_element_by_css(Dashboard._create_s_group_link_css)

        def click_launch_instance_button_from_dashboard(self):
            self.tester.click_element_by_css(self._launch_instance_button_css)

        def get_availability_zone_list(self):
            """
            Gets availability zone list.
            """
            list = self.tester.store_text_by_id(self._availability_zone_dropdown_id)
            list = list[23:]
            list = str(list)
            az_list = list.split()
            return az_list


