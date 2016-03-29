from pages.basepage import BasePage


class CreateASGPage(BasePage):
    def __init__(self, tester):
        self.tester = tester
        self.print_test_context()
        self.verify_create_asg_page_loaded()

    _page_title = "Create new scaling group"
    _name_input_field_id = "name"
    _launch_configuration_selector_id = 'launch_config'
    _min_capacity_field_id = "min_size"
    _desired_capacity_field_id = "desired_capacity"
    _max_capacity_field_id = "max_size"
    _next_button_id = "visit-step-2"
    _next_tab_id = "tabStep2"
    _health_check_grace_period_field_id = "health_check_period"
    _availability_zones_field_css = "#availability_zones_chosen>ul"
    _chosen_availability_zone_close_x_css = 'a[class="search-choice-close"]'
    _create_scaling_group_button_id = "create-scalinggroup-btn"

    def verify_create_asg_page_loaded(self):
        self.tester.wait_for_text_present_by_id(BasePage(self)._page_title_id, self._page_title)
        self.tester.wait_for_element_present_by_id(self._name_input_field_id)

    def create_asg(self, asg_name, launch_config_name=None, availabilityzones=None, min_cpapacity=None,
                   desired_capacity=None, max_capacity=None, grace_period=None, loadbalancers=None):
        self.tester.send_keys_by_id(self._name_input_field_id, asg_name)
        if launch_config_name is not None:
            self.tester.select_by_id(self._launch_configuration_selector_id, launch_config_name)
        if min_cpapacity is not None:
            self.tester.send_keys_by_id(self._min_capacity_field_id, min_cpapacity)
        if desired_capacity is not None:
            self.tester.send_keys_by_id(self._desired_capacity_field_id, desired_capacity)
        if max_capacity is not None:
            self.tester.send_keys_by_id(self._max_capacity_field_id, max_capacity)
        self.tester.click_element_by_id(self._next_tab_id)
        if grace_period is not None:
            self.tester.send_keys_by_id(self._health_check_grace_period_field_id, grace_period)
        if availabilityzones is not None:
            pass
        if loadbalancers is not None:
            pass
        self.tester.click_element_by_id(self._create_scaling_group_button_id)
