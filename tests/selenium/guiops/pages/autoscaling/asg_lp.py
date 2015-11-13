from pages.landingpage import LandingPage


class ASGLanding(LandingPage):
    def __init__(self, tester):
        self.tester = tester
        self.verify_instance_view_page_loaded()

    _asg_landing_page_title = "Scaling groups"
    _create_asg_button_id = "create-scalinggroup-btn"
    _asg_action_menu_id = "table-item-dropdown_{0}" #asg_name_required
    _view_details_actionmenu_item_css = "#item-dropdown_{0}>li>a"  #asg_name required
    _manage_instances_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(2)>a"  #asg_name required
    _manage_policies_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(3)>a"  #asg_name required
    _delete_asg_actions_menu_item_css = "#item-dropdown_{0}>li:nth-of-type(4)>a"  #asg_name required
    _search_input_field_css = ".search-input"

    def verify_asg_lp_loaded(self):
        self.tester.wait_for_text_present_by_id(LandingPage(self)._page_title_id, self._asg_landing_page_title)
        self.tester.wait_for_visible_by_id(LandingPage(self)._refresh_button_id)

    def click_action_create_asg_on_landing_page(self):
        self.tester.click_element_by_id(self._create_asg_button_id)

    def click_action_delete_asg_on_lp(self, asg_name):
        self.tester.click_element_by_id(self._asg_action_menu_id.format(asg_name))
        self.tester.click_element_by_css(self._delete_asg_actions_menu_item_css.format(asg_name))

    def click_action_manage_volumes_on_view_page(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._manage_volumes_actions_menu_item_css.format(instance_id))

    def get_id_of_newly_launched_instance(self, name=None):
        contains_id = self.tester.get_attribute_by_css(self._first_instance_link_in_list_css, "ng-href")
        instance_id = contains_id[-10:]
        print(instance_id)
        return instance_id

    def verify_instance_status_is_running(self, instance_id):
        NotImplementedError

    def goto_instance_detail_page_via_link(self, instance_id):
        self.tester.click_element_by_css(self._instance_link_css.format(instance_id))

    def goto_instance_detail_page_via_actions(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._view_details_actionmenu_item_css.format(instance_id))

    def click_action_launch_more_like_this(self, instance_id):
        self.tester.click_element_by_id(self._instance_action_menu_id.format(instance_id))
        self.tester.click_element_by_css(self._launch_more_like_this_actionmenu_item_css.format(instance_id))

    def get_instance_name(self, instance_id):
        full_name = self.tester.store_text_by_css(self._instance_link_css.format(instance_id))
        instance_name=None
        if len(full_name)>11:
            instance_name = full_name[:-13]
        return instance_name

    def click_terminate_all_instances_button(self):
        self.tester.click_element_by_id(self._terminate_all_instances_btn_id)

    def verify_there_are_no_running_instances(self):
        self.tester.send_keys_by_css(self._search_input_field_css, "running")
        self.tester.wait_for_text_present_by_css(LandingPage(self)._item_count_css,"0")

