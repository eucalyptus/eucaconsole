from pyramid.view import view_config
from pyramid.renderers import render_to_response
from ..views import BaseView


class GenericDirectiveView(object):
    """
    This class is to provide views to serve directives where all that's neeeded is i18n
    """
    def __init__(self, request, **kwargs):
        self.request = request

    @view_config(route_name='render_template')
    def render_template(self):
        template_name = '/'.join(self.request.subpath)
        return render_to_response('eucaconsole.templates:{0}.pt'.format(template_name), {}, request=self.request)
