"""
Layout configuration via pyramid_layout
See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html

"""
from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.security import has_permission


class MasterLayout(object):
    site_title = "Eucalyptus Management Console"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.home_url = request.application_url

    def is_user_admin(self):
        return has_permission('manage', self.context, self.request)

    @reify
    def global_macros(self):
        renderer = get_renderer("templates/macros.pt")
        return renderer.implementation().macros
