from pages.basepage import BasePage



class DeleteBucketModal(BasePage):

    def __init__(self, tester):
        super(DeleteBucketModal, self).__init__(tester)

    _delete_bucket_submit_button_id = 'delete_bucket_submit_button'

    def delete_bucket(self):
        self.tester.click_element_by_id(self._delete_bucket_submit_button_id)


class OpenSharedBucket(BasePage):

    def __init__(self, tester):
        super(OpenSharedBucket, self).__init__(tester)

    _shared_bucket_name_id = 'shared-bucket-name'
    _shared_bucket_save_to_list = 'save-bucket-to-list'
    _open_bucket_btn = 'open-bucket-btn'

    def open_bucket(self, bucket_name=None):
        if bucket_name is not None:
            self.tester.send_keys_by_id(self._shared_bucket_name_id, bucket_name)
        self.tester.click_element_by_id(self._open_bucket_btn)


class DeleteObjectModal(BasePage):

    def __init__(self, tester):
        super(DeleteObjectModal, self).__init__(tester)

    _delete_object_submit_button_id = 'delete-object-btn'

    def delete_object(self):
        self.tester.click_element_by_id(self._delete_object_submit_button_id)


class DeleteEverythingModal(BasePage):

    def __init__(self, tester):
        super(DeleteEverythingModal, self).__init__(tester)

    _delete_everything_submit_button_id = 'delete-all-dialog-btn'

    def delete_all(self):
        self.tester.click_element_by_id(self._delete_everything_submit_button_id)


class DownloadObjectModal(BasePage):

    def __init__(self, tester):
        super(DownloadObjectModal, self).__init__(tester)

    _shared_object_path_id = 'shared-object-path'
    _download_object_btn = 'download-object-btn'

    def download_object(self, object_path):
        self.tester.send_keys_by_id(self._shared_object_path_id, object_path)
        self.tester.click_element_by_id(self._download_object_btn)


class BucketCreateFolderModal(BasePage):
    pass