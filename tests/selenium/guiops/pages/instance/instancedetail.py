from pages.detailpage import DetailPage

class InstanceDetailPage(DetailPage):

    def __init__(self, tester, instance_name = None):
        self.instance_name = instance_name
        self.tester = tester
        self.verify_instance_detail_page_loaded()

    def verify_instance_detail_page_loaded(self):
        pass