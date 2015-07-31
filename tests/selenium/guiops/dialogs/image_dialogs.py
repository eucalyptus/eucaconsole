from pages.basepage import BasePage

class RemoveImageFromCloudDialog(BasePage):

    def __init__(self, tester):
        self.tester = tester

    _delete_associated_snaspshot_checkbox_id = "delete_snapshot"
    _remove_image_from_cloud_submit_button_id = "deregister-image-button"

    def remove_image(self, delete_associated_snapshot=False):
        if delete_associated_snapshot is True:
            self.tester.click_element_by_id(self._delete_associated_snaspshot_checkbox_id)
        self.tester.click_element_by_id(self._remove_image_from_cloud_submit_button_id)


