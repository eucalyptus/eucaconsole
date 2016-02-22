from pages.landingpage import LandingPage
from dialogs.eip_dialogs import DisassociateEipDialog


class EipLanding(LandingPage):
    _elastic_ip_allocate_button_id = 'allocate-ipaddresses-btn'
    _elastic_ip_checkbox_css = '#tableview tr[data-item-id="{0}"] input.item-checkbox'  # Requires EIP
    _elastic_ip_item_row_css_prefix = '#tableview tr[data-item-id="{0}"] td:last-child .actions'  # Requires EIP
    _elastic_ip_actions_menu_css = '{0} a.dropdown'.format(_elastic_ip_item_row_css_prefix)
    _elastic_ip_release_item_css = '{0} a.action-release '.format(_elastic_ip_item_row_css_prefix)
    _more_actions_button_id = 'more-actions-btn'
    _more_actions_release_ip_css = '#more-actions-dropdown a.more-actions-release'
    _more_actions_associate_ip_css = '#item-dropdown_{0}>li>a[ng-click="revealModal(\'associate\', item)"]'
    _more_actions_disassociate_ip_css = '#item-dropdown_{0}>li>a[ng-click="revealModal(\'disassociate\', item)"]'
    _elastic_ip_link_css = 'td>a[href="/ipaddresses/{0}"]'
    _instance_id_link_css = 'td>a[href="/instances/{0}"]'

    def __init__(self, tester):
        super(EipLanding, self).__init__(tester)
        self.tester = tester

    def click_allocate_elastic_ips_button(self):
        self.tester.click_element_by_id(self._elastic_ip_allocate_button_id)

    def click_elastic_ips_checkboxes(self, elastic_ips):
        """
        :param elastic_ips: list of elastic IPs (as strings)
        """
        for elastic_ip in elastic_ips:
            self.tester.click_element_by_css(self._elastic_ip_checkbox_css.format(elastic_ip))

    def select_release_ip_actions_menu_item(self, elastic_ip):
        """ Select "Release" item from actions drop-down (in item row)
        :param elastic_ip:
        """
        self.tester.click_element_by_css(self._elastic_ip_actions_menu_css.format(elastic_ip))
        self.tester.click_element_by_css(self._elastic_ip_release_item_css.format(elastic_ip))

    def select_release_ips_more_actions_item(self):
        self.tester.click_element_by_id(self._more_actions_button_id)
        self.tester.click_element_by_css(self._more_actions_release_ip_css)

    def verify_elastic_ip_is_released(self, elastic_ip):
        self.tester.wait_for_element_not_present_by_css(self._elastic_ip_checkbox_css.format(elastic_ip))

    def click_elastic_ip(self, elastic_ip):
        self.tester.click_element_by_css(self._elastic_ip_link_css.format(elastic_ip))

    def associate_with_instance_actions_menu_item(self, elastic_ip):
        self.tester.click_element_by_css(self._elastic_ip_actions_menu_css.format(elastic_ip))
        elastic_ip = str(elastic_ip.replace(".", "_"))
        self.tester.click_element_by_css(self._more_actions_associate_ip_css.format(elastic_ip))

    def verify_elastic_ip_associate_instance(self, instance_id, elastic_ip):
        self.tester.wait_for_element_present_by_css(self._instance_id_link_css.format(instance_id))
        self.tester.click_element_by_css(self._instance_id_link_css.format(instance_id))
        self.tester.wait_for_element_present_by_link_text(elastic_ip)

    def disassociate_with_instance_actions_menu_item(self, elastic_ip, instance_id):
        self.tester.click_element_by_css(self._elastic_ip_actions_menu_css.format(elastic_ip))
        elastic_ip = str(elastic_ip.replace(".", "_"))
        self.tester.click_element_by_css(self._more_actions_disassociate_ip_css.format(elastic_ip))

    def verify_disassociate_eip_from_lp(self, instance_id):
        self.tester.wait_for_element_not_present_by_css(self._instance_id_link_css.format(instance_id))
