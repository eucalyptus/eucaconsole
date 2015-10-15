from pages.basepage import BasePage



class DeleteBucketModal(BasePage):

    def __init__(self, tester):
        super(DeleteBucketModal, self).__init__(tester)

    _delete_bucket_submit_button_id = 'delete_bucket_submit_button'

    def delete_bucket(self):
        self.tester.click_element_by_id(self._delete_bucket_submit_button_id)