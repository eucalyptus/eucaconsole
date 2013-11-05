"""
Core views

"""


class LandingPageView(object):
    def __init__(self, request):
        self.request = request
        self.display_type = self.request.params.get('display', 'gridview')
        self.filter_fields = []
        self.filter_keys = []
        self.items = []
        self.prefix = '/'
