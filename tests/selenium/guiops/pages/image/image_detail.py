from pages.detailpage import DetailPage

class ImageDetailPage(DetailPage):
    def __init__(self, tester):
        self.tester = tester

    _image_detail_page_title = "Details for image:"

    def is_image_detail_page_loaded(self):
        title = str(self.tester.store_text_by_id(DetailPage(self)._detail_page_title_id))
        if title.startswith(self._image_detail_page_title):
            return True
        else:
            return False

    def verify_image_detail_page_loaded(self):
        title = str(self.tester.store_text_by_id(DetailPage(self)._detail_page_title_id))
        assert title.startswith(self._image_detail_page_title)

    def get_image_id(self):
        image_id = self.tester.store_text_by_css(DetailPage(self)._resource_name_and_id_css)
        return image_id