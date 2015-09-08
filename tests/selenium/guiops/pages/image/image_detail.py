from pages.detailpage import DetailPage


class ImageDetailPage(DetailPage):
    def __init__(self, tester):
        self.tester = tester

    _image_detail_page_title = "Details for image:"

    def get_image_id(self):
        image_id = self.tester.store_text_by_css(DetailPage(self)._resource_name_and_id_css)
        return image_id