from pages.detailpage import BasePage


class CreateStackWizard(BasePage):
    _create_stack_name_field_id = "name"
    _sample_stack_selector_id = "sample-template"

    def __init__(self, tester):
        self.tester = tester

    def create_stack(self, name):
        self.tester.send_keys_by_id(self._create_stack_name_field_id, name)
        import pdb; pdb.set_trace()
        self.tester.select_by_id(self._sample_stack_selector_id, 'Basic Instance')
