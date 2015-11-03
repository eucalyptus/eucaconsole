
import simplejson as json

from pyramid.view import view_config

from ..forms import ChoicesManager
from ..i18n import _
from ..views import BaseView


class TemplateDesign(BaseView):
    TEMPLATE = '../templates/stacks/template_designer.pt'

    # define some common properties for re-use
    KEYPAIR_PROP = dict(
        name='KeyName',
        label=_(u'Keypair'),
        datatype='string',
        required=False
    )
    ZONE_PROP = dict(
        name='AvailabilityZone',
        label=_(u'Availability Zone'),
        datatype='string', required=True
    )
    RESOURCE_DEF = dict(
        EC2=[
            dict(
                name='Instance',
                cfn_type='AWS::EC2::Instance',
                properties=[
                    dict(name='ImageId', label=_(u'Image ID'), datatype='string', required=True),
                    dict(name='InstanceType', label=_(u'Instance Type'), datatype='string', required=True),
                    KEYPAIR_PROP,
                    dict(name='SecurityGroup', label=_(u'Security Group'), datatype='string', required=True),
                    dict(name='UserData', label=_(u'User Data'), datatype='string', required=False),
                    ZONE_PROP,
                    # tags...
                ],
            ),
            dict(
                name='Volume',
                cfn_type='AWS::EC2::Volume',
                properties=[
                    dict(name='Size', label=_(u'Size'), datatype='int', required=True),
                    dict(name='SnapshotId', label=_(u'Snapshot ID'), datatype='string', required=False),
                    ZONE_PROP,
                    # tags...
                ],
            )
        ],
        S3=[
            dict(
                name='Bucket',
                cfn_type='AWS::S3::Bucket',
                properties=[
                    dict(name='BucketName', label=_(u'Bucket Name'), datatype='string', required=True),
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
                    if prop['name'] == 'KeyName':
                        prop['data_url'] = self.request.route_path('keypairs_json')
                    if prop['name'] == 'AvailabilityZone':
                        prop['data_url'] = self.request.route_path('zones_json')
                    if prop['name'] == 'InstanceType':
                        prop['data_url'] = self.request.route_path('instancetypes_json')
        json_opts = dict(
            resources=resources,
        )
        self.render_dict['json_opts'] = BaseView.escape_json(json.dumps(json_opts))
        return self.render_dict

    @view_config(route_name='instancetypes_json', renderer='json', request_method='POST')
    def instancetypes_json(self):
        conn = self.get_connection()
        items = ChoicesManager(conn).instance_types()
        types = []
        for item in items:
            types.append(dict(
                name=item[1],
                id=item[0]
            ))
        return dict(results=types)

    @view_config(route_name='zones_json', renderer='json', request_method='POST')
    def zones_json(self):
        conn = self.get_connection()
        items = ChoicesManager(conn).get_availability_zones(self.region)
        zones = []
        for item in items:
            zones.append(dict(
                name=item.name
            ))
        return dict(results=zones)
