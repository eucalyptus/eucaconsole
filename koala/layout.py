"""
Layout configuration via pyramid_layout
See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html

"""
from pyramid.security import has_permission


class MasterLayout(object):
    page_title = "Eucalyptus Management Console"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.home_url = request.application_url

    def is_user_admin(self):
        return has_permission(self.request, 'manage')
