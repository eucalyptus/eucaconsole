from pages.viewpage import ViewPage

class ImageView(ViewPage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_image_view_page_loaded()

    _image_view_page_title = "Images"
    _image_action_menu_css = "[data-dropdown='item-dropdown_{0}']"  #image_id required
    _view_details_actions_menu_item_css ="#item-dropdown_{0}>li:nth-of-type(1)>a" #image_id required
    _launch_instance_actions_menu_item_css ="#item-dropdown_{0}>li:nth-of-type(4)>a" #image_id required

    def verify_image_view_page_loaded(self):
        self.tester.wait_for_text_present_by_id(ViewPage(self)._page_title_id, self._image_view_page_title)
        self.tester.wait_for_visible_by_id(ViewPage(self)._refresh_button_id)

    def click_action_launch_instance(self, image_id):
        self.tester.click_element_by_css(self._image_action_menu_css.format(image_id))
        self.tester.click_element_by_css(self._launch_instance_actions_menu_item_css.format(image_id))