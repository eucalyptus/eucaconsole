from pages.viewpage import ViewPage

class ImageView(ViewPage):

    def __init__(self, tester):
        self.tester = tester
        self.verify_image_view_page_loaded()

    _

    def verify_image_view_page_loaded(self):
        pass
