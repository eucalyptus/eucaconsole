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
        self.tester.wait_for_enabled_by_id(self._allocate_elastic_ips_button_id)
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


class AssociateEipDialog(BasePage):
    _associate_elastic_ips_button_id = 'associate_ip_submit_button'
    _associate_ip_to_instance_button_id = 'associate_ip_to_instance_submit_button'
    _select_instance_css = '#instance_id_chosen a.chosen-single'
    _select_eip_address_css = '#ip_address_chosen a.chosen-single'
    _instance_input_css = '.chosen-search>input'
    _highlighted_search_result_css = '.active-result'
    _notification_css = '#notifications .message'

    def associate_eip_with_instance(self, instance_name):
        self.tester.click_element_by_css(self._select_instance_css)
        self.tester.send_keys_by_css(self._instance_input_css, instance_name)
        self.tester.click_element_by_css(self._highlighted_search_result_css)
        self.tester.click_element_by_id(self._associate_elastic_ips_button_id)
        notification = self.tester.store_text_by_css(self._notification_css)
        notification = notification.replace('Successfully associated IP', '')
        notification = notification.replace('with instance', '')
        return [data.strip() for data in notification.split(',')]

    def associate_eip_from_instance(self, elastic_ip):
        self.tester.click_element_by_css(self._select_eip_address_css)
        self.tester.send_keys_by_css(self._instance_input_css, elastic_ip)
        self.tester.click_element_by_css(self._highlighted_search_result_css)
        self.tester.click_element_by_id(self._associate_ip_to_instance_button_id)
        notification = self.tester.store_text_by_css(self._notification_css)
        notification = notification.replace('Successfully associated IP', '')
        notification = notification.replace('with instance', '')
        return [data.strip() for data in notification.split(',')]


class DisassociateEipDialog(BasePage):
    _disassociate_elastic_ip_button_id = 'disassociate_ip_submit_button'
    _disassociate_elastic_ip_to_instance_button_css = 'button#disassociate_ip_to_instance_submit_button'
    _notification_css = '#notifications .message'

    def disassociate_eip(self):
        self.tester.click_element_by_id(self._disassociate_elastic_ip_button_id)
        notification = self.tester.store_text_by_css(self._notification_css)
        notification = notification.replace('Successfully disassociated IP', '')
        notification = notification.replace('from instance', '')
        return sorted([ip.strip() for ip in notification.split(',')])

    def disassociate_eip_from_instance(self):
        self.tester.click_element_by_css(self._disassociate_elastic_ip_to_instance_button_css)
        notification = self.tester.store_text_by_css(self._notification_css)
        notification = notification.replace('Successfully disassociated the IP', '')
        notification = notification.replace('from the instance', '')
        return sorted([ip.strip() for ip in notification.split(',')])
