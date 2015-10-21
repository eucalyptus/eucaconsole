from pages.detailpage import BasePage


class BucketContentsPage(BasePage):

    def __init__(self, tester, bucket_name):
        super(BucketContentsPage, self).__init__(tester)
        self.bucket_name = bucket_name
        self.verify_bucket_contents_page()

    _bucket_contents_page_title_id = 'pagetitle'
    _bucket_contents_upload_button_id = 'upload-file-btn'
    _bucket_contents_delete_all_button_id = 'delete-all-btn'
    _bucket_item_action_menu_id = '#table-item-dropdown_{0}_{1}'
    _delete_object_bucket_actions_menuitem_css = "#item-dropdown_{0}_{1} a.delete-object"
    _delete_folder_bucket_actions_menuitem_css = "#item-dropdown_{0}_{1} a.delete-folder"

    def verify_bucket_contents_page(self):
        self.tester.driver.switch_to.window(
            self.tester.driver.window_handles[0])

    def verify_object_in_bucket(self, object_name):
        self.tester.wait_for_element_present_by_link_text(object_name)

    def click_upload_object_button(self):
        self.tester.click_element_by_id(self._bucket_contents_upload_button_id)

    def click_action_delete_object_in_bucket(self, object_name):
        self.tester.click_element_by_css(
            self._bucket_item_action_menu_id.format(self.bucket_name, object_name))
        self.tester.click_element_by_css(
            self._delete_object_bucket_actions_menuitem_css.format(
                self.bucket_name, object_name))

    def delete_all_objects_in_bucket(self):
        self.tester.click_element_by_id(self._bucket_contents_delete_all_button_id)
