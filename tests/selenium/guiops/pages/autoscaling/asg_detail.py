from pages.detailpage import DetailPage


class ASGDetailPage(DetailPage):

    def __init__(self, tester):
        self.tester = tester

    _asg_detail_page_title = "Details for scaling group: {0}" #asg name required
    _next_step_modal_id = "nextstep-scalinggroup-modal"
    _do_notshow_again_checkbox_id = "check-do-not-show-me-again"
    _close_modal_x_css = "#nextstep-scalinggroup-modal>a.close-reveal-modal"
    _scaling_history_tab_css = "[href='/scalinggroups/{0}/history']" #asg name required
    _scaling_policies_tab_css = "[href='/scalinggroups/{0}/policies']" #asg name required
    _instances_tab_css = "[href='/scalinggroups/{0}/instances']" #asg name required
    _general_tab_css = '[href="/scalinggroups/{0}"]' #asg name required
    _active_tab_css ="dd.active"
    _delete_asg_action_menuitem_id = "delete-scalinggroup-action"
    _save_changes_button_id = "save-changes-btn"
    _min_capacity_field_id = "min_size"
    _desired_capacity_field_id = "desired_capacity"
    _max_capacity_field_id = "max_size"
    _launch_config_dropdown_css = "#launch_config_chosen>a"
    _launch_config_search_field_css = "#launch_config_chosen>div>div>input"
    _launch_config_search_active_result_css = "li.active-result.result-selected"
    _scaling_history_row_expando_css = "i.table-expando-closed:nth-of-type(1)"
    _scaling_history_first_cause_css = "tbody:nth-of-type(1)>tr:nth-of-type(2)>td:nth-of-type(2)>div:nth-of-type(2)>div:nth-of-type(2)>div:nth-of-type(1)"



    def verify_asg_detail_page_loaded(self, asg_name):
        """
        Waits for the asg detail page title to appear; waits for actions menu to become visible. Closes the next step modal.
        """
        if self.tester.check_visibility_by_id(self._next_step_modal_id):
            self.tester.click_element_by_id(self._do_notshow_again_checkbox_id)
            self.tester.click_element_by_css(self._close_modal_x_css)
        self.tester.wait_for_text_present_by_id(DetailPage(self)._detail_page_title_id, self._asg_detail_page_title.format(asg_name))
        self.tester.wait_for_element_present_by_css(DetailPage(self)._actions_menu_css)

    def goto_scaling_history_tab(self, asg_name):
        """
        Checks if Scaling History tab is already open. Opens Scaling History tab if not.
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab in ['General', 'Instances', 'Scaling Policies']:
            self.tester.click_element_by_css(self._scaling_history_tab_css.format(asg_name))
        elif tab == "Scaling History":
            pass
        else:
            print "ERROR: tab {0} not among recognized tab names.".format(tab)

    def goto_instances_tab(self, asg_name):
        """
        Checks if Instances tab is already open. Opens Instances tab if not.
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab in ['General', 'Scaling Policies', 'Scaling History']:
            self.tester.click_element_by_css(self._instances_tab_css.format(asg_name))
        elif tab == "Instances":
            pass
        else:
            print "ERROR: tab {0} not among recognized tab names.".format(tab)

    def goto_general_tab(self, asg_name):
        """
        Checks if General tab is already open. Opens general tab if not.
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab in ['Instances', 'Scaling Policies', 'Scaling History']:
            self.tester.click_element_by_css(self._general_tab_css.format(asg_name))
        elif tab == "General":
            pass
        else:
            print "ERROR: tab {0} not among recognized tab names.".format(tab)

    def goto_scaling_policies_tab(self, asg_name):
        """
        Checks if Scaling Policies tab is already open. Opens Scaling Policies tab if not.
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab in ['General', 'Instances', 'Scaling History']:
            self.tester.click_element_by_css(self._scaling_policies_tab_css.format(asg_name))
        elif tab == "Scaling Policies":
            pass
        else:
            print "ERROR: tab {0} not among recognized tab names.".format(tab)

    def click_action_delete_asg_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_asg_action_menuitem_id)

    def change_capacity_on_detail_page(self, min=None, desired=None, max=None):
        if min is not None:
            self.tester.send_keys_by_id(self._min_capacity_field_id, min)
        if max is not None:
            self.tester.send_keys_by_id(self._max_capacity_field_id, max)
        if desired is not None:
            self.tester.send_keys_by_id(self._desired_capacity_field_id, desired)
        self.tester.click_element_by_id(self._save_changes_button_id)

    def change_launch_configuration_on_detail_page(self, asg_name, launch_config_name):
        self.goto_general_tab(asg_name)
        self.tester.click_element_by_css(self._launch_config_dropdown_css)
        self.tester.send_keys_by_css(self._launch_config_search_field_css,launch_config_name)
        self.tester.click_element_by_css(self._launch_config_search_active_result_css)
        self.tester.click_element_by_id(self._save_changes_button_id)

    def verify_scaling_history(self, asg_name):
        self.goto_scaling_history_tab(asg_name)
        self.tester.click_element_by_css(self._scaling_history_row_expando_css)
        text = self.tester.store_text_by_css(self._scaling_history_first_cause_css)
        if text.find('an instance was started') > 0:
            print 'Found expected cause {0}'.format(text)
        else:
            print 'ERROR: couldn\'t find expected scaling history cause text'

