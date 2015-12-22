from pages.detailpage import DetailPage

class EipDetailPage(DetailPage):

    def __init__(self, tester, elastic_ip):
        self.elastic_ip_addr = elastic_ip
        self.tester = tester
        self.verify_eip_detail_page_loaded()

    _elastic_ips_detail_page_title = "Details for IP address: {0}"
    _release_ip_address_menuitem_id = "release-ip-action"

    def verify_eip_detail_page_loaded(self):
        self.tester.wait_for_text_present_by_id(DetailPage._detail_page_title_id, self._elastic_ips_detail_page_title.
                                                format(self.elastic_ip_addr))
        self.tester.wait_for_visible_by_css(DetailPage._actions_menu_css)

    def click_action_release_ip_address_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._release_ip_address_menuitem_id)