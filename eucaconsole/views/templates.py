
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from ..views import BaseView, JSONResponse, JSONError

class TemplateDesign(BaseView):
    TEMPLATE = '../templates/stacks/template_designer.pt'

    def __init__(self, request):
        super(TemplateDesign, self).__init__(request)
        self.render_dict = dict()

    @view_config(route_name='template_designer', renderer=TEMPLATE)
    def stack_view(self):
        return self.render_dict
