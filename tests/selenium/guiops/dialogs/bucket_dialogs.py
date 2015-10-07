from pages.basepage import BasePage


class CreateBucketDialog(BasePage):

    def __init__(self, tester):
        super(CreateBucketDialog, self).__init__(tester)

    _bucket_name_field_id = 'bucket_name'
    _create_bucket_id = 'create_bucket_submit_button'

    def create_bucket(self, bucket_name=None):
        if bucket_name is not None:
            self.tester.send_keys_by_id(self._bucket_name_field_id, bucket_name)
        self.tester.click_element_by_id(self._create_bucket_id)


class DeleteBucketModal(BasePage):

    def __init__(self, tester):
        super(DeleteBucketModal, self).__init__(tester)

    _delete_bucket_submit_button_id = 'delete_bucket_submit_button'

    def delete_bucket(self):
        self.tester.click_element_by_id(self._delete_bucket_submit_button_id)