from pages.basepage import BasePage

class CreateLaunchConfigPage(BasePage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_create_lc_page_loaded()

    _page_title = "Create new launch configuration"
    _image_search_field_css = "input.search-input"
    _first_image_button_css = ".button.tiny.round"
    _name_input_field_id = "name"
    _instance_type_selector_id = "instance_type"
    _user_data_text_radio_bttn_css = "#inputtype[value = 'text']"
    _user_data_text_input_field_id = "userdata"
    _user_data_file_radio_bttn_css = "#inputtype[value = 'file']"
    _user_data_file_upload_id = "userdata_file"

    _launch_configuration_selector_id = 'launch_config'
    _min_capacity_field_id = "min_size"
    _desired_capacity_field_id = "desired_capacity"
    _max_capacity_field_id = "max_size"
    _next_button_id = "visit-step-2"
    _health_check_grace_period_field_id = "health_check_period"
    _availability_zones_field_css = "#availability_zones_chosen>ul"
    _chosen_availability_zone_close_x_css = 'a[class="search-choice-close"]'
    _create_scaling_group_button_id = "create-scalinggroup-btn"

    instance_types = {"m1.small": "m1.small: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)",
                       "t1.micro": "t1.micro: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)",
                       "m1.medium": "m1.medium: 1 CPUs, 512 memory (MB), 10 disk (GB,root device)",
                       "c1.medium": "c1.medium: 2 CPUs, 512 memory (MB), 10 disk (GB,root device)",
                       "m1.large": "m1.large: 2 CPUs, 512 memory (MB), 10 disk (GB,root device)",
                       "m1.xlarge": "m1.xlarge: 2 CPUs, 1024 memory (MB), 10 disk (GB,root device)",
                       "c1.xlarge": "c1.xlarge: 2 CPUs, 2048 memory (MB), 10 disk (GB,root device)",
                       "m2.xlarge": "m2.xlarge: 2 CPUs, 2048 memory (MB), 10 disk (GB,root device)",
                       "m3.xlarge": "m3.xlarge: 4 CPUs, 2048 memory (MB), 15 disk (GB,root device)",
                       "m2.2xlarge": "m2.2xlarge: 2 CPUs, 4096 memory (MB), 30 disk (GB,root device)",
                       "m3.2xlarge": "m3.2xlarge: 4 CPUs, 4096 memory (MB), 30 disk (GB,root device)",
                       "cc1.4xlarge": "cc1.4xlarge: 8 CPUs, 3072 memory (MB), 60 disk (GB,root device)",
                       "m2.4xlarge": "m2.4xlarge: 8 CPUs, 4096 memory (MB), 60 disk (GB,root device)",
                       "hi1.4xlarge": "hi1.4xlarge: 8 CPUs, 6144 memory (MB), 120 disk (GB,root device)",
                       "cc2.8xlarge": "cc2.8xlarge: 16 CPUs, 6144 memory (MB), 120 disk (GB,root device)",
                       "cg1.4xlarge": "cg1.4xlarge: 16 CPUs, 12288 memory (MB), 200 disk (GB,root device)",
                       "cr1.8xlarge": "cr1.8xlarge: 16 CPUs, 16384 memory (MB), 240 disk (GB,root device)",
                       "hs1.8xlarge": "hs1.8xlarge: 48 CPUs, 119808 memory (MB), 24000 disk (GB,root device)"}


    def verify_create_lc_page_loaded(self):
        self.tester.wait_for_text_present_by_id(BasePage(self)._page_title_id, self._page_title)


    def create_new_launch_config(self, lc_name, instance_type="t1.micro: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)", image="centos", availabilityzones = None, min_cpapacity=None, desired_capacity=None, max_capacity=None, grace_period=None, loadbalancers=None, user_data=None):

        self.tester.send_keys_by_css(self._image_search_field_css, image)
        self.tester.click_element_by_css(self._first_image_button_css)

        self.tester.send_keys_by_id(self._name_input_field_id, lc_name)
        if instance_type is not None:
            self.tester.select_by_id(self._instance_type_selector_id, self.instance_types.get(instance_type))
        if user_data is not None:
            self.tester.click_element_by_css(self._user_data_text_radio_bttn_css)
            self.send_keys_by_id(self._user_data_text_input_field_id, user_data)





        if min_cpapacity is not None:
            self.tester.send_keys_by_id(self._min_capacity_field_id, min_cpapacity)
        if desired_capacity is not None:
            self.tester.send_keys_by_id(self._desired_capacity_field_id, desired_capacity)
        if max_capacity is not None:
            self.tester.send_keys_by_id(self._max_capacity_field_id, max_capacity)
        self.tester.click_element_by_id(self._next_button_id)
        if grace_period is not None:
            self.tester.send_keys_by_id(self._health_check_grace_period_field_id, grace_period)
        if availabilityzones is not None:
            pass
        if loadbalancers is not None:
            pass
        self.tester.click_element_by_id(self._create_scaling_group_button_id)




