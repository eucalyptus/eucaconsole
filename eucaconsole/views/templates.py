
import logging
import simplejson as json

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from ..i18n import _
from ..views import BaseView, JSONResponse, JSONError

class TemplateDesign(BaseView):
    TEMPLATE = '../templates/stacks/template_designer.pt'

    # define some common properties for re-use
    KEYPAIR_PROP = dict(
        name='keypair',
        label=_(u'Keypair'),
        datatype='string',
        required=False
    )
    RESOURCE_DEF = dict(
        EC2=[
            dict(name='Instance',
                cfn_type='AWS::EC2::Instance',
                properties=[
                    dict(name='name', label=_(u'Name'), datatype='string', required=False),
                    dict(name='image_id', label=_(u'Image ID'), datatype='string', required=True),
                    dict(name='min', label=_(u'Min'), datatype='int', required=True),
                    dict(name='max', label=_(u'Max'), datatype='int', required=True),
                    dict(name='instance_type', label=_(u'Instance Type'), datatype='string', required=True),
                    KEYPAIR_PROP,
                    dict(name='security_group', label=_(u'Security Group'), datatype='string', required=True),
                    dict(name='userdata', label=_(u'User Data'), datatype='string', required=False),
                    # tags...
                ],
            ),
            dict(name='Volume',
                cfn_type='AWS::EC2::Volume',
                properties=[
                    dict(name='Size', label=_(u'Size'), datatype='int', required=True),
                    dict(name='SnapshotId', label=_(u'Snapshot ID'), datatype='string', required=False),
                    dict(name='AvailabilityZone', label=_(u'Availability Zone'), datatype='string', required=True),
                    # tags...
                ],
            )
        ]
    )

    def __init__(self, request):
        super(TemplateDesign, self).__init__(request)
        self.render_dict = dict()

    @view_config(route_name='template_designer', renderer=TEMPLATE)
    def stack_view(self):
        resources = self.RESOURCE_DEF
        # populate data urls for values that can come from cloud
        for service in resources:
            for res in resources[service]:
                for prop in res['properties']:
                    if prop['name'] == 'SnapshotId':
                        prop['data_url'] = self.request.route_path('snapshots_json')
                    if prop['name'] == 'KeyPair':
                        prop['data_url'] = self.request.route_path('keypairs_json')
                    #if prop['name'] == 'AvailabilityZone':
                    #    prop['data_url'] = self.request.route_path('zones_json')
        json_opts = dict(
            resources=resources,
        )
        self.render_dict['json_opts'] = BaseView.escape_json(json.dumps(json_opts))
        return self.render_dict
