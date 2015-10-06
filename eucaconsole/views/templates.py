
import logging
import simplejson as json

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from ..i18n import _
from ..views import BaseView, JSONResponse, JSONError

class TemplateDesign(BaseView):
    TEMPLATE = '../templates/stacks/template_designer.pt'

    RESOURCE_DEF = dict(
        EC2=[
            dict(name='Instance',
            ),
            dict(name='Volume',
                properties=[
                    dict(name='size', label=_(u'Size'), datatype='int', required=True)
                ],
            )
        ],
        AutoScaling=[
            dict(name='AutoScalingGroup',
            ),
            dict(name='LaunchConfiguration',
            )
        ]
    )

    def __init__(self, request):
        super(TemplateDesign, self).__init__(request)
        self.render_dict = dict()

    @view_config(route_name='template_designer', renderer=TEMPLATE)
    def stack_view(self):
        json_opts = dict(
            resources=self.RESOURCE_DEF,
        )
        self.render_dict['json_opts'] = BaseView.escape_json(json.dumps(json_opts))
        return self.render_dict
