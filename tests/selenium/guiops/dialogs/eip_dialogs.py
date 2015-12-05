from pages.basepage import BasePage


class AllocateEipDialog(BasePage):

    _allocate_elastic_ips_number_input_css = '#allocate-ip-modal form input[name="ipcount"]'
    _allocate_elastic_ips_button_id = 'allocate-ipaddresses-dialog-btn'
    _release_elastic_ips_button_id = 'release_ipaddresses-dialog-btn'
    _notification_css = '#notifications .message'

    def __init__(self, tester):
        super(AllocateEipDialog, self).__init__(tester)
        self.tester = tester

    def allocate_elastic_ips(self, number=1):
        """
        :param number: how many IPs to allocate
        :return: allocated IPs as a sorted list of strings
        """
        self.tester.wait_for_element_present_by_id(self._allocate_elastic_ips_button_id)
        self.tester.send_keys_by_css(self._allocate_elastic_ips_number_input_css, str(number))
        self.tester.click_element_by_id(self._allocate_elastic_ips_button_id)
        notification = self.tester.store_text_by_css(self._notification_css)
        allocated_ips = notification.replace('Successfully allocated IPs', '').strip()
        return sorted([ip.strip() for ip in allocated_ips.split(',')])

    def release_elastic_ips(self):
        """
        :return: release IPs as a sorted list of strings
        """
        self.tester.wait_for_element_present_by_id(self._release_elastic_ips_button_id)
        self.tester.click_element_by_id(self._release_elastic_ips_button_id)
        notification = self.tester.store_text_by_css(self._notification_css)
        released_ips = notification.replace('Successfully released', '')
        return sorted([ip.strip() for ip in released_ips.split(',')])
