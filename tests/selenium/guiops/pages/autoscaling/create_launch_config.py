from pages.basepage import BasePage
from pages.autoscaling.create_asg import CreateASGPage

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
    _create_asg_from_lc_chckbox_id = "create_sg_from_lc"
    _advanced_options_link_id = "visit-step-4"
    _kernel_selector_id = "kernel_id"
    _ramdisk_selector_id = "ramdisk_id"
    _enable_monitoring_chckbox_id = "monitoring_enabled"
    _create_lc_submit_step4_btn_id = "create-launchconfig-btn-step4"
    _create_lc_submit_step3_btn_id = "create-launchconfig-btn-step3"

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


    def create_new_launch_config(self, lc_name, instance_type=None, image="centos", key_name="None (advanced option)",
                               security_group="default", user_data_text=None, user_data_file_path=None, role=None, create_asg=False, kernel_id=None, ramdisk_id=None,
                               enable_monitoring=True):

        self.tester.send_keys_by_css(self._image_search_field_css, image)
        self.tester.click_element_by_css(self._first_image_button_css)
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
        if create_asg is not False:
            pass
        else:
            self.tester.click_element_by_id(self._create_asg_from_lc_chckbox_id)
        if (kernel_id is not None) or (ramdisk_id is not None) or (enable_monitoring is not True):
            self.tester.click_element_by_id(self._advanced_options_link_id)
            if kernel_id is not None:
                self.tester.select_by_id(self._kernel_selector_id, kernel_id)
            if ramdisk_id is not None:
                self.tester.select_by_id(self._ramdisk_selector_id, ramdisk_id)
            if enable_monitoring is not True:
                self.tester.click_element_by_id(self._enable_monitoring_chckbox_id)
            self.tester.click_element_by_id(self._create_lc_submit_step4_btn_id)
        else:
            self.tester.click_element_by_id(self._create_lc_submit_step3_btn_id)

    def create_new_launch_config_and_asg(self, lc_name, asg_name, instance_type=None, image="centos", key_name="None (advanced option)",
                               security_group="default", user_data_text=None, user_data_file_path=None, role=None, create_asg=True, kernel_id=None, ramdisk_id=None,
                               enable_monitoring=True, availabilityzones = None, min_cpapacity=None, desired_capacity=None, max_capacity=None, grace_period=None, loadbalancers=None):
        self.create_new_launch_config(lc_name, instance_type, image, key_name,
                               security_group, user_data_text, user_data_file_path, role, create_asg, kernel_id, ramdisk_id, enable_monitoring)
        CreateASGPage(self.tester).create_asg(asg_name, availabilityzones, min_cpapacity, desired_capacity,
                                      max_capacity, grace_period, loadbalancers)












