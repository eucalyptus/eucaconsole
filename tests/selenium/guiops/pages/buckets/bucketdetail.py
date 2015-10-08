from pages.detailpage import DetailPage


class BucketDetailPage(DetailPage):

    def __init__(self, tester, bucket_name):
        self.bucket_name = bucket_name
        self.tester = tester
        self.verify_bucket_detail_page_loaded()

    _bucket_detail_page_title = 'Details for bucket: {0}'
    _delete_bucket_action_menuitem_id = 'delete-bucket-action'
    _view_contents_action_menuitem_id = 'view-contents-action'
    _create_folder_action_menuitem_id = 'create-folder-action'
    _upload_file_action_menuitem_id = 'upload-file-action'
    _propagate_permissions_checkbox_id = 'propagate_acls'

    _share_account_chosen_id = 'share_account_chosen'
    _share_account_selectors = {
        'anyone': '#share_account_chosen li.chosen-results[data-option-array-index="1"]',
        'authusers': '#share_account_chosen li.chosen-results[data-option-array-index="1"]'
    }

    _share_permission_chosen_id = 'share_permission_chosen'
    _share_permission_selectors = {
        'fullcontrol': '#share_permission_chosen li.chosen-results[data-option-array-index="0"]',
        'viewdownload': '#share_permission_chosen li.chosen-results[data-option-array-index="1"]',
        'createdelete': '#share_permission_chosen li.chosen-results[data-option-array-index="2"]',
        'readsharing': '#share_permission_chosen li.chosen-results[data-option-array-index="3"]',
        'writesharing': '#share_permission_chosen li.chosen-results[data-option-array-index="4"]'
    }

    _share_add_grantee_button_id = 'add-s3acl-button'

    def verify_bucket_detail_page_loaded(self):
        self.tester.wait_for_text_present_by_id(
            DetailPage._detail_page_title_id,
            self._bucket_detail_page_title.format(self.bucket_name))

    def click_action_view_contents_on_detail_page(self):
        self.tester.click_element_by_css(self._actions_menu_css)
        self.tester.click_element_by_id(self._view_contents_action_menuitem_id)

    def click_action_create_folder_on_detail_page(self):
        self.tester.click_element_by_css(self._actions_menu_css)
        self.tester.click_element_by_id(self._create_folder_action_menuitem_id)

    def click_action_upload_files_on_detail_page(self):
        self.tester.click_element_by_css(self._actions_menu_css)
        self.tester.click_element_by_id(self._upload_file_action_menuitem_id)

    def click_action_delete_bucket_on_detail_page(self):
        self.tester.click_element_by_css(self._actions_menu_css)
        self.tester.click_element_by_id(self._delete_bucket_action_menuitem_id)

    def click_propagate_permissions_on_detail_page(self):
        self.tester.click_element_by_id(self._propagate_permissions_checkbox_id)

    def click_share_account_on_detail_page(self, account='anyone'):
        self.tester.click_element_by_id(self._share_account_chosen_id)
        self.driver.find_element_by_css_selector(
            self._share_account_selectors[account]).click()

    def click_share_permission_on_detail_page(self, permission='fullcontrol'):
        self.tester.click_element_by_id(self._share_permission_chosen_id)
        self.driver.find_element_by_css_selector(
            self._share_permission_selectors[permission]).click()
