from pages.detailpage import DetailPage


class LaunchConfigDetailPage(DetailPage):

    def __init__(self, tester):
        self.tester = tester

    _lc_detail_page_title = "Details for launch configuration: {0}" #lc name required
    _delete_lc_action_menuitem_id = "delete-launchconfig-action"



    def verify_lc_detail_page_loaded(self, lc_name):
        """
        Waits for the lc detail page title to appear; waits for actions menu to become visible.
        """
        self.tester.wait_for_text_present_by_id(DetailPage(self)._detail_page_title_id, self._lc_detail_page_title.format(lc_name))
        self.tester.wait_for_element_present_by_css(DetailPage(self)._actions_menu_css)

    def goto_instances_tab(self, asg_name):
        """
        Checks if Instances tab is already open. Opens Instances tab if not.
        """
        tab = self.tester.store_text_by_css(self._active_tab_css)
        print "Found active tab {0}".format(tab)
        if tab == "General" or tab == "Scaling Policies":
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
        if tab == "Instances" or tab == "Scaling Policies":
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
        if tab == "General" or tab == "Instances":
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








