from pages.landingpage import LandingPage


class EipLanding(LandingPage):
    _elastic_ip_checkbox_css = '#tableview tr[data-item-id="{0}"] input.row-checkbox'  # Requires Elastic IP
    _more_actions_button_id = 'more-actions-btn'
    _more_actions_release_ip_css = '#more-actions-dropdown a.more-actions-release'

    def __init__(self, tester):
        super(EipLanding, self).__init__(tester)
        self.tester = tester

    def click_elastic_ips_checkboxes(self, elastic_ips):
        """
        :param elastic_ips: list of elastic IPs (as strings)
        """
        for elastic_ip in elastic_ips:
            self.tester.click_element_by_css(self._elastic_ip_checkbox_css.format(elastic_ip))

    def select_release_ips_more_actions_item(self):
        self.tester.wait_for_clickable_by_id(self._more_actions_button_id)
        self.tester.click_element_by_id(self._more_actions_button_id)
        self.tester.click_element_by_css(self._more_actions_release_ip_css)
