import time

from pages.detailpage import DetailPage
from selenium.common.exceptions import ElementNotVisibleException


class ASGDetailPage(DetailPage):
    MONITORING_CHARTS_LIST = [
        # ASG Metrics
        {'metric': 'GroupTotalInstances', 'statistic': 'Maximum'},
        {'metric': 'GroupInServiceInstances', 'statistic': 'Maximum'},
        {'metric': 'GroupMinSize', 'statistic': 'Maximum'},
        {'metric': 'GroupMaxSize', 'statistic': 'Maximum'},
        {'metric': 'GroupDesiredCapacity', 'statistic': 'Maximum'},
        {'metric': 'GroupPendingInstances', 'statistic': 'Maximum'},
        {'metric': 'GroupTerminatingInstances', 'statistic': 'Maximum'},
        # Instance metrics
        {'metric': 'CPUUtilization', 'statistic': 'Average'},
        {'metric': 'DiskReadBytes', 'statistic': 'Average'},
        {'metric': 'DiskReadOps', 'statistic': 'Average'},
        {'metric': 'DiskWriteBytes', 'statistic': 'Average'},
        {'metric': 'DiskWriteOps', 'statistic': 'Average'},
        {'metric': 'NetworkIn', 'statistic': 'Average'},
        {'metric': 'NetworkOut', 'statistic': 'Average'},
    ]

    def __init__(self, tester):
        self.tester = tester
        self.print_test_context()

    _asg_detail_page_title = "Details for scaling group: {0}"  # asg name required
    _next_step_modal_id = "nextstep-scalinggroup-modal"
    _do_notshow_again_checkbox_id = "check-do-not-show-me-again"
    _close_modal_x_css = "#nextstep-scalinggroup-modal .close-reveal-modal"
    _scaling_history_tab_css = "[href='/scalinggroups/{0}/history']"  # asg name required
    _scaling_policies_tab_css = "[href='/scalinggroups/{0}/policies']"  # asg name required
    _instances_tab_css = "[href='/scalinggroups/{0}/instances']"  # asg name required
    _monitoring_tab_css = "[href='/scalinggroups/{0}/monitoring']"  # asg name required
    _general_tab_css = '[href="/scalinggroups/{0}"]'  # asg name required
    _active_tab_css = "dd.active"
    _ec2_charts_container_id = 'charts-container-ec2'
    _autoscaling_charts_container_id = 'charts-container-autoscaling'
    _enable_metrics_collection_button_id = "enable-metrics-collection-btn"
    _delete_asg_action_menuitem_id = "delete-scalinggroup-action"
    _save_changes_button_id = "save-changes-btn"
    _min_capacity_field_id = "min_size"
    _desired_capacity_field_id = "desired_capacity"
    _max_capacity_field_id = "max_size"
    _launch_config_dropdown_css = "#launch_config_chosen>a"
    _launch_config_search_field_css = "#launch_config_chosen>div>div>input"
    _launch_config_search_active_result_css = "li.active-result.result-selected"
    _scaling_history_first_row_expando_css = "i.table-expando-closed:nth-of-type(1)"
    _scaling_history_first_cause_css = "tbody:nth-of-type(1)>tr:nth-of-type(2)>td:nth-of-type(2)>div:nth-of-type(2)>div:nth-of-type(2)>div:nth-of-type(1)"

    def verify_asg_detail_page_loaded(self, asg_name):
        """
        Waits for the asg detail page title to appear; waits for actions menu to become visible. Closes the next step modal.
        """
        self.confirm_scaling_policy_modal()
        self.tester.wait_for_text_present_by_id(DetailPage(self)._detail_page_title_id,
                                                self._asg_detail_page_title.format(asg_name))
        self.tester.wait_for_element_present_by_css(DetailPage(self)._actions_menu_css)

    def goto_scaling_history_tab(self, asg_name):
        """
        Checks if Scaling History tab is already open. Opens Scaling History tab if not.
        """
        _refresh_button_css_in_history_tab = "#refresh-btn"
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab != "Scaling history":
            self.tester.click_element_by_css_robust(self._scaling_history_tab_css.format(asg_name), _refresh_button_css_in_history_tab)
        else:
            pass

    def goto_instances_tab(self, asg_name):
        """
        Checks if Instances tab is already open. Opens Instances tab if not.
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab != "Instances":
            self.tester.click_element_by_css(self._instances_tab_css.format(asg_name))
        else:
            pass

    def goto_monitoring_tab(self, asg_name):
        """
        Checks if Monitoring tab is already open. Opens tab if not.
        :param asg_name:
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab != "Monitoring":
            self.tester.click_element_by_css(self._monitoring_tab_css.format(asg_name))
        else:
            pass

    def goto_general_tab(self, asg_name):
        """
        Checks if General tab is already open. Opens general tab if not.
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab != "General":
            self.tester.click_element_by_css(self._general_tab_css.format(asg_name))
        else:
            pass

    def goto_scaling_policies_tab(self, asg_name):
        """
        Checks if Scaling Policies tab is already open. Opens Scaling Policies tab if not.
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab != "Scaling policies":
            self.tester.click_element_by_css(self._scaling_policies_tab_css.format(asg_name))
        else:
            pass

    def click_action_delete_asg_on_detail_page(self):
        self.tester.click_element_by_css(DetailPage._actions_menu_css)
        self.tester.click_element_by_id(self._delete_asg_action_menuitem_id)

    def change_capacity_on_detail_page(self, min_capacity=None, desired_capacity=None, max_capacity=None):
        if min_capacity is not None:
            self.tester.send_keys_by_id(self._min_capacity_field_id, min_capacity)
            self.tester.click_element_by_id(self._min_capacity_field_id)  # Validation error workaround
        if max_capacity is not None:
            self.tester.send_keys_by_id(self._max_capacity_field_id, max_capacity)
            self.tester.click_element_by_id(self._max_capacity_field_id)  # Validation error workaround
        if desired_capacity is not None:
            self.tester.send_keys_by_id(self._desired_capacity_field_id, desired_capacity)
            self.tester.click_element_by_id(self._desired_capacity_field_id)  # Validation error workaround
        time.sleep(1)
        try:
            self.tester.click_element_by_id(self._save_changes_button_id)
            is_visible = self.tester.check_visibility_by_css(DetailPage(self)._notification_css)
            if not is_visible:
                print "Hitting enter on Save Changes button"
                self.tester.send_keys_by_id(self._save_changes_button_id,"\n", clear_field=False)
        except Exception,e:
            print "ERROR: Could not Save Changes"
            raise

    def verify_capacity_entries(self, min_capacity=0, desired_capacity=0, max_capacity=0):
        min_field_value = self.tester.driver.find_element_by_id(self._min_capacity_field_id).get_attribute('value')
        desired_field_value = self.tester.driver.find_element_by_id(
                self._desired_capacity_field_id).get_attribute('value')
        max_field_value = self.tester.driver.find_element_by_id(self._max_capacity_field_id).get_attribute('value')
        assert min_capacity == int(min_field_value)
        assert desired_capacity == int(desired_field_value)
        assert max_capacity == int(max_field_value)

    def change_launch_configuration_on_detail_page(self, asg_name, launch_config_name):
        self.goto_general_tab(asg_name)
        self.tester.click_element_by_css(self._launch_config_dropdown_css)
        self.tester.send_keys_by_css(self._launch_config_search_field_css, launch_config_name)
        self.tester.click_element_by_css(self._launch_config_search_active_result_css)
        self.tester.click_element_by_id(self._save_changes_button_id)

    def verify_scaling_history(self, asg_name):
        self.confirm_scaling_policy_modal()
        self.goto_scaling_history_tab(asg_name)
        self.tester.click_element_by_css_robust(
            self._scaling_history_first_row_expando_css, self._scaling_history_first_cause_css)
        text = self.tester.store_text_by_css(self._scaling_history_first_cause_css)
        if text.find('an instance was started') > 0:
            print 'Found expected cause {0}'.format(text)
        else:
            print "ERROR: couldn't find expected scaling history cause text"

    def enable_metrics_collection(self, asg_name):
        self.confirm_scaling_policy_modal()
        self.goto_monitoring_tab(asg_name)
        if self.tester.check_visibility_by_id(self._enable_metrics_collection_button_id):
            self.tester.click_element_by_id(self._enable_metrics_collection_button_id)

    def verify_charts_on_monitoring_page(self, asg_name):
        self.confirm_scaling_policy_modal()
        self.goto_monitoring_tab(asg_name)
        self.tester.wait_for_element_present_by_id(self._ec2_charts_container_id)
        self.tester.wait_for_element_present_by_id(self._autoscaling_charts_container_id)
        for chart in self.MONITORING_CHARTS_LIST:
            chart_id = 'cwchart-{0}-{1}'.format(chart.get('metric'), chart.get('statistic'))
            self.tester.wait_for_element_present_by_id(chart_id)

   # def _confirm_scaling_policy_modal(self):
   #     if self.tester.check_visibility_by_id(self._next_step_modal_id):
   #         self.tester.click_element_by_id(self._do_notshow_again_checkbox_id)
   #         self.tester.click_element_by_css(self._close_modal_x_css)

    def confirm_scaling_policy_modal(self):
        """
        Selects "do not show me again" on the scaling policy modal.
        """
        if self.tester.check_visibility_by_id(self._next_step_modal_id):
            time.sleep(1)
            if self.tester.check_visibility_by_id(self._do_notshow_again_checkbox_id):
                print "Confirmed: Scaling policy modal checkbox is visible"

                if self.tester.check_visibility_by_css(self._close_modal_x_css):
                    print "Confirmed: Scaling policy modal close button is visible"

                    try:
                        self.tester.click_element_by_id(self._do_notshow_again_checkbox_id)
                    except ElementNotVisibleException:
                        print "ERROR: element by id = {0} not visible".format(self._do_notshow_again_checkbox_id)

                    finally:
                        is_selected = self.tester.verify_selected_by_id(self._do_notshow_again_checkbox_id)
                        i=1
                        while (i<3) and not is_selected:
                            try:
                                time.sleep(1)
                                is_selected = self.tester.verify_selected_by_id(self._do_notshow_again_checkbox_id)
                                time.sleep(1)
                                if is_selected:
                                    break
                                self.tester.click_element_by_id(self._do_notshow_again_checkbox_id)
                            except Exception,e:
                                print "Click on Do not show again dialog checkbox failed"
                            is_selected = self.tester.verify_selected_by_id(self._do_notshow_again_checkbox_id)
                        self.tester.click_element_by_css_resilient(self._close_modal_x_css, self._close_modal_x_css)
                else:
                    print "Confirmed: Scaling policy modal close button is NOT visible"
            else:
                print "Confirmed: Scaling policy modal checkbox is NOT visible"