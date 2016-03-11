import time
from pages.detailpage import BasePage


class UpdateStack(BasePage):
    _edit_template_css = ".edit-template"
    _save_template_button_css = ".save-template-btn"
    _next_step_button_id = "visit-step-2"
    _param_instancetype_selector_id = "InstanceType_chosen"
    _param_instancetype_search_field_css = "#InstanceType_chosen>div.chosen-drop>div.chosen-search>input"
    _update_stack_button_id = "stack-update-btn-step2"

    def __init__(self, tester):
        self.tester = tester

    def update_stack(self):
        time.sleep(4)
        # edit template
        self.tester.click_element_by_css(self._edit_template_css)
        self.tester.click_element_by_css(self._save_template_button_css)
        # modify parameter
        self.tester.click_element_by_id(self._param_instancetype_selector_id)
        self.tester.send_keys_by_css(self._param_instancetype_search_field_css, 'm1.large\n')

        self.tester.click_element_by_id(self._update_stack_button_id)
