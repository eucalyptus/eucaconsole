from pages.detailpage import BasePage


class CreateStackWizard(BasePage):
    _create_stack_name_field_id = "name"
    _sample_stack_selector_id = "sample-template"
    _url_input_radiobutton_id = "inputtype-url"
    _url_input_field_id = "template-url"
    _next_step_button_id = "visit-step-2"
    _param_keyname_selector_id = "KeyName"
    _param_imageid_selector_id = "ImageId_chosen"
    _param_imageid_search_field_css = "#ImageId_chosen>div.chosen-drop>div.chosen-search>input"
    _create_from_snapshot_search_field_css = ".chosen-search>input"
    _create_stack_button_id = "stack-wizard-btn-step2"

    def __init__(self, tester):
        self.tester = tester

    def create_stack(self, name, template_url=None):
        # populate first step
        self.tester.send_keys_by_id(self._create_stack_name_field_id, name)
        if template_url is None:
            self.tester.select_by_id(self._sample_stack_selector_id, 'Basic Instance')
        else:
            self.tester.click_element_by_id(self._url_input_radiobutton_id)
            self.tester.send_keys_by_id(self._url_input_field_id, template_url)
        self.tester.wait_for_clickable_by_id(self._next_step_button_id)
        self.tester.click_element_by_id(self._next_step_button_id)
        # populate second step
        self.tester.select_by_id(self._param_keyname_selector_id, index=0)
        self.tester.click_element_by_id(self._param_imageid_selector_id)
        self.tester.send_keys_by_css(self._param_imageid_search_field_css, 'precise\n')

        self.tester.click_element_by_id(self._create_stack_button_id)
