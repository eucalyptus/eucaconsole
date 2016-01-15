from pages.detailpage import DetailPage

class InstanceDetailPage(DetailPage):

    def __init__(self, tester, instance_id, instance_name=None):
        self.instance_name = instance_name
        self.instance_id = instance_id
        self.tester = tester
        self.verify_instance_detail_page_loaded()

    _terminate_instance_action_item_id = "terminate-instance-action"
    _volumes_tab_css = 'dd:nth-of-type(2)>a'
    _attach_volume_tile_css = ".plus"
    _instance_status_css = "[class='label radius status {0}']"  #instance status is required
    _launch_more_like_this_action_menuitem_id = "launchmore-instance-action"
    _associate_ip_address_action_menuitem_id = "associate-ip-to-instance-action"
    _disassociate_ip_address_action_menuitem_id = "disassociate-ip-from-instance-action"
    _attached_volume_status_xpath = '//a[@href="/volumes/{0}"]/../../../div[@class="footer status attached"]'  #requires volume id
    _elastic_ip_link_css = 'a[href="/ipaddresses/{0}"]'

    def verify_instance_detail_page_loaded(self):
        if self.instance_name == None:
            instance_name_full = self.instance_id
        else:
            instance_name_full = self.instance_name + " (" + self.instance_id + ")"
        self.tester.wait_for_text_present_by_id(DetailPage(self)._detail_page_title_id, instance_name_full)

    def verify_action_menu_loaded(self):
        self.tester.wait_for_element_present_by_css(DetailPage(self)._actions_menu_css)

    def click_terminate_instance_action_item_from_detail_page(self):
        self.tester.click_element_by_css(DetailPage(self)._actions_menu_css)
        self.tester.click_element_by_id(self._terminate_instance_action_item_id)

    def verify_instance_is_in_running_state(self, timeout_in_seconds=240):
        self.tester.wait_for_visible_by_css(self._instance_status_css.format("running"), timeout_in_seconds)

    def verify_instance_is_terminated(self, timeout_in_seconds=240):
        self.tester.wait_for_visible_by_css(self._instance_status_css.format("terminated"), timeout_in_seconds)

    def click_action_launch_more_like_this(self):
        self.tester.click_element_by_css(DetailPage(self)._actions_menu_css)
        self.tester.click_element_by_id(self._launch_more_like_this_action_menuitem_id)

    def click_action_attach_volume(self):
        self.tester.click_element_by_css(self._volumes_tab_css)
        self.tester.click_element_by_css(self._attach_volume_tile_css)

    def verify_volume_is_attached(self, volume_id, timeout_in_seconds=240):
        self.tester.click_element_by_css(self._volumes_tab_css)
        self.tester.wait_for_visible_by_xpath(self._attached_volume_status_xpath.format(volume_id), timeout_in_seconds)

    def click_action_associate_ip_address(self):
        self.tester.click_element_by_css(DetailPage(self)._actions_menu_css)
        self.tester.click_element_by_id(self._associate_ip_address_action_menuitem_id)

    def verify_eip_address_associated_to_instance(self, elastic_ip):
        self.tester.wait_for_element_present_by_css(self._elastic_ip_link_css.format(elastic_ip))

    def click_action_disassociate_ip_address(self):
        self.tester.click_element_by_css(DetailPage(self)._actions_menu_css)
        self.tester.click_element_by_id(self._disassociate_ip_address_action_menuitem_id)

    def verify_eip_address_disassociated_to_instance(self, elastic_ip):
        self.tester.wait_for_element_not_present_by_css(self._elastic_ip_link_css.format(elastic_ip))
