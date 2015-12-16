from pages.landingpage import LandingPage

class ImageLanding(LandingPage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_image_view_page_loaded()

    _image_view_page_title = "Images"
    _image_action_menu_css = "[data-dropdown='item-dropdown_{0}']"  #image_id required
    _view_details_actions_menu_item_css ="#item-dropdown_{0}>li:nth-of-type(1)>a" #image_id required
    _launch_instance_actions_menu_item_css ="#item-dropdown_{0}>li:nth-of-type(4)>a" #image_id required
    _remove_image_from_cloud_menu_ietm_css = "#item-dropdown_{0}>li:nth-of-type(6)>a" #image_id required
    _search_input_css = ".search-input"
    _action_menu_of_first_image_in_list_css = "[class='grid-action']"
    _launch_instance_actions_menu_item_for_first_in_list_css = "[class ='f-dropdown open f-open-dropdown']>li:nth-of-type(4)>a"
    _first_image_link_css=".id.breakword"

    def verify_image_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(LandingPage(self)._page_title_id, self._image_view_page_title)
        self.tester.wait_for_visible_by_id(LandingPage(self)._refresh_button_id)

    def click_action_launch_instance(self, image_id_or_type):
        if image_id_or_type[:4] == "emi-":
            self.tester.click_element_by_css(self._image_action_menu_css.format(image_id_or_type))
            self.tester.click_element_by_css(self._launch_instance_actions_menu_item_css.format(image_id_or_type))
        else:
            self.tester.send_keys_by_css(self._search_input_css, image_id_or_type)
            self.tester.click_element_by_css(self._action_menu_of_first_image_in_list_css)
            self.tester.click_element_by_css(self._launch_instance_actions_menu_item_for_first_in_list_css)

    def click_action_remove_image_from_cloud(self, image_id):
        self.tester.click_element_by_css(self._image_action_menu_css.format(image_id))
        self.tester.click_element_by_css(self._remove_image_from_cloud_menu_ietm_css.format(image_id))

    def get_image_id_by_name(self, image_name):
        self.tester.send_keys_by_css(self._search_input_field_css, image_name)
        image_id = self.tester.store_text_by_css(self._first_image_link_css)
        return image_id