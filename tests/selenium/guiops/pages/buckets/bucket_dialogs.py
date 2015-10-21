from pages.basepage import BasePage



class DeleteBucketModal(BasePage):

    def __init__(self, tester):
        super(DeleteBucketModal, self).__init__(tester)

    _delete_bucket_submit_button_id = 'delete_bucket_submit_button'

    def delete_bucket(self):
        self.tester.click_element_by_id(self._delete_bucket_submit_button_id)


class DeleteObjectModal(BasePage):

    def __init__(self, tester):
        super(DeleteObjectModal, self).__init__(tester)

    _delete_object_submit_button_id = 'delete-object-btn'

    def delete_object(self):
        self.tester.click_element_by_id(self._delete_object_submit_button_id)


class BucketCreateFolderModal(BasePage):
    pass