from dialogs.basedialog import BaseDialog

class LaunchInstanceWidget(BaseDialog):

    def __init__(self, tester):
        self.tester = tester

    _image_search_field_css = ".search-input"
    _centos_image_select_button_css = "tr.ng-scope>td.btns>a"
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
    _launch_instance_button_id = "launch-instance-btn-step3"

    def launch_centos_instance(self, availability_zone = None, instance_type = "t1.micro: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)", number_of_of_instances = None, name = None, key_name = "None (advanced option)", security_group = "default"):
        self.tester.send_keys_by_css(self._image_search_field_css, "centos")
        self.tester.click_element_by_css(self._centos_image_select_button_css)
        if number_of_of_instances != None:
            self.send_keys_by_css(self._number_of_instances_input_field_id, number_of_of_instances)
        if instance_type != None:
            self.tester.select_by_id(self._instance_type_selector_id, instance_type)
        if availability_zone != None:
            self.tester.select_by_id(self._availability_zone_selector_id, availability_zone)
        if name != None:
            self.tester.send_keys_by_css(self._name_input_field_css, name)
        self.tester.click_element_by_id(self._step2_next_button_id)
        self.tester.select_by_id(self._keypair_selector_id, key_name)
        self.tester.click_element_by_css(self._security_group_choices_css)
        self.tester.send_keys_by_css(self._security_group_search_field_css, security_group)
        self.tester.click_element_by_css(self._highlighted_security_group_css)
        self.tester.click_element_by_id(self._launch_instance_button_id)

class TerminateInstance(BaseDialog):

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
        self.tester.wait_for_text_not_present_by_css(self._instance_id_in_modal_css, instance_full_name)
        self.tester.click_element_by_id(self._terminate_instance_submit_button_id)







