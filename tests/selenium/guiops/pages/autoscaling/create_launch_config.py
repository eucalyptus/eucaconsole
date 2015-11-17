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
    _next_button_step2_id = "visit-step-3"
    _next_button_step1_id = "visit-step-2"
    _keypair_selector_id = "keypair"
    _security_group_selector_id = "securitygroup_chosen"
    _security_group_choices_css = "ul.chosen-choices"
    _security_group_search_field_css = "ul.chosen-choices>li.search-field>input"
    _highlighted_security_group_css = "[class = 'active-result highlighted']"
    _security_group_choice_close_css = ".search-choice-close"
    _role_selector_id = "role"



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


    def create_new_launch_config(self, lc_name, instance_type="t1.micro: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)", image="centos", key_name="None (advanced option)",
                               security_group="default", user_data_text=None, user_data_file_path=None, role=None):

        self.tester.send_keys_by_css(self._image_search_field_css, image)
        self.tester.click_element_by_css(self._first_image_button_css)
        self.tester.click_element_by_id(self._next_button_step1_id)
        self.tester.send_keys_by_id(self._name_input_field_id, lc_name)
        if instance_type is not None:
            self.tester.select_by_id(self._instance_type_selector_id, self.instance_types.get(instance_type))
        if user_data_text is not None:
            self.tester.click_element_by_css(self._user_data_text_radio_bttn_css)
            self.send_keys_by_id(self._user_data_text_input_field_id, user_data_text)
        if user_data_file_path is not None:
            self.tester.click_element_by_css(self._user_data_file_radio_bttn_css)
            pass
        self.tester.click_element_by_id(self._next_button_step2_id)
        self.tester.select_by_id(self._keypair_selector_id, key_name)
        while self.tester.check_visibility_by_css(self._security_group_choice_close_css):
            self.tester.click_element_by_css(self._security_group_choice_close_css)
        self.tester.click_element_by_id(self._security_group_selector_id)
        self.tester.send_keys_by_css(self._security_group_search_field_css, security_group)
        self.tester.click_element_by_css(self._highlighted_security_group_css)
        if role is not None:
            self.tester.select_by_id(self._role_selector_id, role)










