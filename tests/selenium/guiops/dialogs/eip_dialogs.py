from pages.basepage import BasePage


class AllocateEipDialog(BasePage):

    _allocate_elastic_ips_number_input_css = '#allocate-ip-modal form input[name="ipcount"]'
    _allocate_elastic_ips_button_id = 'allocate-ipaddresses-dialog-btn'
    _notification_css = '#notifications .message'

    def allocate_elastic_ips(self, number=1):
        """
        :param number: how many IPs to allocate
        :return: allocated IPs as a sorted list of strings
        """
        self.tester.send_keys_by_css(self._allocate_elastic_ips_number_input_css, str(number))
        self.tester.click_element_by_id(self._allocate_elastic_ips_button_id)
        notification = self.tester.store_text_by_css(self._notification_css)
        notification = notification.replace('Successfully allocated IPs', '').strip()
        return sorted([ip.strip() for ip in notification.split(',')])


class ReleaseEipDialog(BasePage):
    _release_elastic_ips_button_id = 'release_ip_submit_button'
    _notification_css = '#notifications .message'

    def release_elastic_ips(self):
        """
        :return: released IPs as a sorted list of strings
        """
        self.tester.click_element_by_id(self._release_elastic_ips_button_id)
        notification = self.tester.store_text_by_css(self._notification_css)
        notification = notification.replace('Successfully released', '')
        notification = notification.replace('to the cloud', '')
        return sorted([ip.strip() for ip in notification.split(',')])
