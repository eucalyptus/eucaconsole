from dialogs.basedialog import BaseDialog

class LaunchInstanceWizard(BaseDialog):

    def __init__(self, tester):
        self.tester = tester

    _image_search_field_css = ".search-input"
    _first_image_button_css = "tr.ng-scope>td.btns>a"
    _number_of_instances_input_field_id = "number"
    _instance_type_selector_id = "instance_type"
    _availability_zone_selector_id = "zone"
    _name_input_field_css = "[class='name ng-pristine ng-untouched ng-valid']"
    _step2_next_button_id = "visit-step-3"
    _keypair_selector_id = "keypair"
    _security_group_selector_id = "securitygroup_chosen"
    _security_group_choices_css = "ul.chosen-choices"
    _security_group_search_field_css = "ul.chosen-choices>li.search-field>input"
    _highlighted_security_group_css = "[class = 'active-result highlighted']"
    _launch_instance_button_step3_id = "launch-instance-btn-step3"
    _launch_instance_button_step4_id = "launch-instance-btn-step4"
    _user_data_text_radio_bttn_css ="#inputtype[value = 'text']"
    _user_data_text_input_field_id ="userdata"
    _advanced_options_link_id = "visit-step-4"
    _enable_monitoring_checkbox_id = "monitoring_enabled"
    _use_private_addressing_only_checkbox_id ="private_addressing"
    _security_group_choice_close_css=".search-choice-close"

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

    def launch_instance(self, image="centos", availability_zone=None,
                               instance_type="t1.micro: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)",
                               number_of_of_instances=None, instance_name=None, key_name="None (advanced option)",
                               security_group="default", user_data=None, monitoring=False, private_addressing=False):
        self.tester.send_keys_by_css(self._image_search_field_css, image)
        self.tester.click_element_by_css(self._first_image_button_css)
        self.launch_instance_step2(availability_zone, instance_type,number_of_of_instances,instance_name,key_name,
                                   security_group,user_data,monitoring,private_addressing)

    def launch_instance_step2(self, availability_zone=None,
                               instance_type="t1.micro: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)",
                               number_of_of_instances=None, instance_name=None, key_name="None (advanced option)",
                               security_group="default", user_data=None, monitoring=False, private_addressing=False):

        if number_of_of_instances is not None:
            self.tester.send_keys_by_id(self._number_of_instances_input_field_id, number_of_of_instances)
        if instance_type is not None:
            self.tester.select_by_id(self._instance_type_selector_id, self.instance_types.get(instance_type))
        if availability_zone is not None:
            self.tester.select_by_id(self._availability_zone_selector_id, availability_zone)
        if instance_name is not None:
            self.tester.send_keys_by_css(self._name_input_field_css, instance_name)
        if user_data is not None:
            self.tester.click_element_by_css(self._user_data_text_radio_bttn_css)
            self.send_keys_by_id(self._user_data_text_input_field_id, user_data)
        self.tester.wait_for_clickable_by_id(self._step2_next_button_id)
        self.tester.click_element_by_id(self._step2_next_button_id)
        self.tester.select_by_id(self._keypair_selector_id, key_name)
        while self.tester.check_visibility_by_css(self._security_group_choice_close_css):
            self.tester.click_element_by_css(self._security_group_choice_close_css)
        self.tester.click_element_by_id(self._security_group_selector_id)
        self.tester.send_keys_by_css(self._security_group_search_field_css, security_group)
        self.tester.click_element_by_css(self._highlighted_security_group_css)
        if monitoring or private_addressing:
            self.tester.click_element_by_id(self._advanced_options_link_id)
            if monitoring:
                self.tester.click_element_by_id(self._enable_monitoring_checkbox_id)
            if private_addressing:
                self.tester.click_element_by_id(self._use_private_addressing_only_checkbox_id)
            self.tester.click_element_by_id(self._launch_instance_button_step4_id)
        else:
            self.tester.click_element_by_id(self._launch_instance_button_step3_id)


class TerminateInstanceModal(BaseDialog):

    def __init__(self, tester):
        self.tester = tester

    _terminate_instance_submit_button_id = "terminate_instance_submit_button"
    _instance_id_in_modal_css ="#terminate-instance-modal>div>p>strong"

    def click_terminate_instance_submit_button(self, instance_id,  instance_name=None):
        """
        Waits for instance id appear in the modal. Clicks terminate submit button.
        :param instance_id:
        """
        if instance_name != None:
            instance_full_name = instance_name + " (" + instance_id +")"
        else:
            instance_full_name = instance_id
        self.tester.wait_for_text_present_by_css(self._instance_id_in_modal_css, instance_full_name)
        self.tester.click_element_by_id(self._terminate_instance_submit_button_id)


class LaunchMoreLikeThisDialog(BaseDialog):

    def __init__(self, tester):
        self.tester = tester

    _launch_instance_button_id = "save-changes-btn"
    _instance_name_field_css = "[class='name ng-scope']"
    _advanced_options_css = "#advanced-section>h6>a"
    _help_expando_css = "#help-expando>div>a"
    _enable_monitoring_chkbox_id = "monitoring_enabled"
    _use_private_addressing_chkbox_id = "private_addressing"
    _user_data_text_radio_button_css = "#inputtype[value='text']"
    _user_data_text_input_field_id = "userdata"

    def launch_more_like_this(self, instance_name=None, user_data=None, monitoring=False, private_addressing=False):
        if instance_name is not None:
            self.tester.send_keys_by_css(self._instance_name_field_css, instance_name)
        if user_data is not None:
            self.tester.click_element_by_css(self._user_data_text_radio_button_css)
            self.tester.send_keys_by_id(self._user_data_text_input_field_id, user_data)
        if monitoring or private_addressing:
            self.tester.click_element_by_css(self._advanced_options_css)
            if monitoring:
                self.tester.click_element_by_id(self._enable_monitoring_chkbox_id)
            if private_addressing:
                self.tester.click_element_by_id(self._use_private_addressing_chkbox_id)
        self.tester.click_element_by_id(self._launch_instance_button_id)

class TerminateAllInstancesModal(BaseDialog):

    def __init__(self, tester):
        self.tester = tester

    _terminate_all_instances_submit_btn_id = "terminate_all_instances_submit_button"

    def click_terminate_all_instances_submit_button(self):
        self.tester.click_element_by_id(self._terminate_all_instances_submit_btn_id)






