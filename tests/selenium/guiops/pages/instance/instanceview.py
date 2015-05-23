from pages.viewpage import ViewPage

class InstanceView(ViewPage):



    def __init__(self, tester):
        self.tester = tester
        self.verify_instance_view_page_loaded()

    def verify_instance_view_page_loaded(self):
        pass
