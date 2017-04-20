# -*- coding: utf-8 -*-
# Copyright 2015-2017 Ent. Services Development Corporation LP
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Pyramid views for Eucalyptus and AWS CloudWatch metrics

"""
import copy
import simplejson as json

from pyramid.view import view_config

from ..constants.cloudwatch import (
    MONITORING_DURATION_CHOICES, METRIC_TITLE_MAPPING, STATISTIC_CHOICES, GRANULARITY_CHOICES,
    DURATION_GRANULARITY_CHOICES_MAPPING, METRIC_TYPES
)
from ..i18n import _
from ..views import LandingPageView, BaseView, TaggedItemView
from . import boto_error_handler


RESOURCE_LABELS = {
    'AutoScalingGroupName': _(u'Auto scaling group'),
    'InstanceId': _(u'Instance'),
    'InstanceType': _(u'Instance type'),
    'ImageId': _(u'Image'),
    'VolumeId': _(u'Volume'),
    'LoadBalancerName': _(u'Load balancer'),
    'AvailabilityZone': _(u'Availability zone'),
}

STD_NAMESPACES = ['AWS/EC2', 'AWS/EBS', 'AWS/ELB', 'AWS/AutoScaling', 'AWS/S3']

METRIC_CATEGORIES = [
    dict(
        name='scalinggroupmetrics',
        label=_(u'Auto scaling group - Group metrics'),
        namespace='AWS/AutoScaling',
        resource=['AutoScalingGroupName'],
    ),
    dict(
        name='ebs',
        label=_(u'EBS - Per volume'),
        namespace='AWS/EBS',
        resource=None,
    ),
    dict(
        name='ec2instance',
        label=_(u'EC2 - Per-instance'),
        namespace='AWS/EC2',
        resource=['InstanceId'],
    ),
    dict(
        name='ec2allinstances',
        label=_(u'EC2 - Across all instances'),
        namespace='AWS/EC2',
        resource=['InstanceId'],
    ),
    dict(
        name='scalinggroupinstancemetrics',
        label=_(u'EC2 - Instance metrics by scaling group'),
        namespace='AWS/EC2',
        resource=['AutoScalingGroupName'],
    ),
    dict(
        name='ec2instancetype',
        label=_(u'EC2 - Per instance type'),
        namespace='AWS/EC2',
        resource=['InstanceType'],
    ),
    dict(
        name='ec2image',
        label=_(u'EC2 - Per image'),
        namespace='AWS/EC2',
        resource=['ImageId'],
    ),
    dict(
        name='elb',
        label=_(u'ELB - Per LB'),
        namespace='AWS/ELB',
        resource=['LoadBalancerName'],
    ),
    dict(
        name='elbzone',
        label=_(u'ELB - Per zone'),
        namespace='AWS/ELB',
        resource=['AvailabilityZone'],
    ),
    dict(
        name='elbandzone',
        label=_(u'ELB - Per LB / Per zone'),
        namespace='AWS/ELB',
        resource=['AvailabilityZone', 'LoadBalancerName'],
    ),
    dict(
        name='elball',
        label=_(u'ELB - Across all load balancers'),
        resource=['LoadBalancerName'],
        namespace='AWS/ELB',
    ),
    dict(
        name='custom',
        label=_(u'Custom metrics'),
        namespace=None,
        resource=None,
    ),
]

METRICS_FOR_ASG = [
    'GroupDesiredCapacity',
    'GroupInServiceInstances',
    'GroupMaxSize',
    'GroupMinSize',
    'GroupPendingInstances',
    'GroupTerminatingInstances',
    'GroupTotalInstances'
]

METRICS_FOR_INSTANCE = [
    'CPUUtilization',
    'DiskReadBytes',
    'DiskReadOps',
    'DiskWriteBytes',
    'DiskWriteOps',
    'NetworkIn',
    'NetworkOut',
    'StatusCheckFailed',
    'StatusCheckFailed_Instance',
    'StatusCheckFailed_System'
]

METRICS_FOR_ELB = [
    'HealthyHostCount',
    'UnHealthyHostCount'
]

METRICS_FOR_VOLUME = [
    'VolumeConsumedReadWriteOps',
    'VolumeIdleTime',
    'VolumeQueueLength',
    'VolumeReadBytes',
    'VolumeReadOps',
    'VolumeThroughputPercentage',
    'VolumeTotalReadTime',
    'VolumeTotalWriteTime',
    'VolumeWriteBytes',
    'VolumeWriteOps'
]


class CloudWatchMetricsView(LandingPageView):
    """CloudWatch Metrics landing page view"""
    TEMPLATE = '../templates/cloudwatch/metrics.pt'

    def __init__(self, request):
        super(CloudWatchMetricsView, self).__init__(request)
        self.title_parts = [_(u'Metrics')]
        self.initial_sort_key = 'res_name'
        self.prefix = '/cloudwatch/metrics'
        self.cloudwatch_conn = self.get_connection(conn_type='cloudwatch')
        self.filter_keys = ['metric_label', 'resources']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='res_name', name=_(u'Resource name: A to Z')),
            dict(key='-res_name', name=_(u'Resource name: Z to A')),
            dict(key='metric_name', name=_(u'Metric name: A to Z')),
            dict(key='-metric_name', name=_(u'Metric name: Z to A')),
        ]
        search_facets = [
            {'name': 'cat_name', 'label': _(u'Resource type'), 'options': [
                {'key': cat['name'], 'label': cat['label']} for cat in METRIC_CATEGORIES
            ]},
            {'name': 'metric_name', 'label': _(u'Scaling group metric'), 'options': [
                {'key': metric, 'label': METRIC_TITLE_MAPPING[metric]} for metric in METRICS_FOR_ASG
            ]},
            {'name': 'metric_name', 'label': _(u'Instance metric'), 'options': [
                {'key': metric, 'label': METRIC_TITLE_MAPPING[metric]} for metric in METRICS_FOR_INSTANCE
            ]},
            {'name': 'metric_name', 'label': _(u'Load balancer metric'), 'options': [
                {'key': metric, 'label': METRIC_TITLE_MAPPING[metric]} for metric in METRICS_FOR_ELB
            ]},
            {'name': 'metric_name', 'label': _(u'Volume metric'), 'options': [
                {'key': metric, 'label': METRIC_TITLE_MAPPING[metric]} for metric in METRICS_FOR_VOLUME
            ]}
        ]
        self.render_dict = dict(
            filter_keys=self.filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.request.route_path('cloudwatch_metrics_json'),
            json_item_names_endpoint=self.request.route_path('cloudwatch_resource_names_json'),
            categories_json=json.dumps([cat['name'] for cat in METRIC_CATEGORIES]),
            statistic_choices=STATISTIC_CHOICES,
            duration_choices=MONITORING_DURATION_CHOICES,
            chart_options_json=self.get_chart_options_json()
        )

    @view_config(route_name='cloudwatch_metrics', renderer=TEMPLATE, request_method='GET')
    def metrics_landing(self):
        return self.render_dict

    @staticmethod
    def get_chart_options_json():
        return BaseView.escape_json(json.dumps({
            'metric_title_mapping': METRIC_TITLE_MAPPING,
            'granularity_choices': GRANULARITY_CHOICES,
            'duration_granularities_mapping': DURATION_GRANULARITY_CHOICES_MAPPING,
            'largeChart': True
        }))


class CloudWatchGraphView(LandingPageView):
    """CloudWatch Metrics mobile graph-only view"""
    TEMPLATE = '../templates/cloudwatch/metricgraph.pt'

    def __init__(self, request):
        super(CloudWatchGraphView, self).__init__(request)
        self.title_parts = [_(u'Graph')]
        self.render_dict = dict(
            statistic_choices=STATISTIC_CHOICES,
            duration_choices=MONITORING_DURATION_CHOICES,
            chart_options_json=CloudWatchMetricsView.get_chart_options_json()
        )

    @view_config(route_name='cloudwatch_graph', renderer=TEMPLATE, request_method='GET')
    def metrics_landing(self):
        return self.render_dict


class CloudWatchMetricsJsonView(BaseView):
    """JSON response for CloudWatch Metrics landing page et. al."""
    @view_config(route_name='cloudwatch_metrics_json', renderer='json', request_method='POST')
    def cloudwatch_metrics_json(self):
        categories = copy.deepcopy(METRIC_CATEGORIES)
        with boto_error_handler(self.request):
            items = self.get_items()
            metrics = []
            for cat in categories:
                if cat['name'] in ['ec2instancetype', 'ec2image'] and self.request.session['cloud_type'] == 'aws':
                    cat['label'] = cat['label'] + _(u' (requires detailed monitoring on AWS)')
                namespace = cat['namespace']
                if namespace:
                    tmp = [{
                        'name': item.name,
                        'namespace': item.namespace,
                        'dimensions': item.dimensions
                    } for item in items if item.namespace == namespace and item.dimensions]
                else:
                    tmp = [{
                        'name': item.name,
                        'namespace': item.namespace,
                        'dimensions': item.dimensions
                    } for item in items if item.namespace not in STD_NAMESPACES]
                if cat['name'] in ['ec2allinstances', 'elball']:
                    tmp = set([(met['name'], met['namespace']) for met in tmp])
                    tmp = [([], met[0], met[1]) for met in tmp]
                else:
                    tmp = [(met['dimensions'].items(), met['name'], met['namespace']) for met in tmp]
                cat_metrics = []
                for metric in tmp:
                    metric_name = metric[1]
                    metric_dims = metric[0]
                    if cat['name'] in ['ec2allinstances', 'elball']:
                        res_ids = []
                        res_types = []
                        unit = [mt['unit'] for mt in METRIC_TYPES if mt['name'] == metric]
                    else:
                        res_ids = [dim[1][0] for dim in metric_dims]
                        res_types = [dim[0] for dim in metric_dims]
                        if cat['resource'] and cat['resource'] != res_types:
                            continue
                        unit = [mt['unit'] for mt in METRIC_TYPES if mt['name'] == metric[1]]
                        if cat['name'] == 'custom':
                            unit = ['None']
                    cat_metrics.append(dict(
                        cat_name=cat['name'],
                        namespace=metric[2],
                        id=metric_name + '-' + '-'.join([dim[1][0] for dim in metric_dims]).replace('.', '-'),
                        resources=[dict(
                            res_id=dim[1][0],
                            res_name=dim[1][0],
                            res_type=dim[0],
                            res_type_label=RESOURCE_LABELS[dim[0]] if dim[0] in RESOURCE_LABELS else dim[0],
                            res_url=self.get_url_for_resource(self.request, dim[0], dim[1][0])
                        ) for dim in metric_dims],
                        res_ids=res_ids,
                        res_types=res_types,
                        unit=unit[0] if unit else '',
                        metric_name=metric_name,
                        metric_label=METRIC_TITLE_MAPPING.get(metric_name) or metric_name
                    ))
                metrics.append(dict(
                    heading=True,
                    cat_name=cat['name'],
                    cat_label=cat['label'],
                    cat_total=len(cat_metrics)
                ))
                metrics.extend(cat_metrics)

            return dict(results=metrics)

    @view_config(route_name='cloudwatch_resource_names_json', renderer='json', xhr=True, request_method='POST')
    def cloudwatch_resource_names_json(self):
        ids = self.request.params.getall('id')
        res_type = self.request.params.get('restype')
        names = {}
        if res_type == 'instance':
            instances = self.get_connection().get_only_instances(filters={'instance_id': ids})
            for instance in instances:
                names[instance.id] = (TaggedItemView.get_display_name(instance), instance.tags.get('Name', instance.id))
        elif res_type == 'image':
            region = self.request.session.get('region')
            images = self.get_images(self.get_connection(), [], [], region)
            for image in images:
                names[image.id] = (image.name, image.name)
        elif res_type == 'volume':
            volumes = self.get_connection().get_all_volumes(filters={'volume_id': ids})
            for volume in volumes:
                names[volume.id] = (TaggedItemView.get_display_name(volume), volume.tags.get('Name', volume.id))
        return dict(results=names)

    @view_config(route_name='metrics_available_for_dimensions', renderer='json', request_method='GET')
    def metrics_available_for_resource(self):
        dimensions_param = self.request.params.get('dimensions', '{}')
        dimensions = json.loads(dimensions_param)
        namespace_param = self.request.params.get('namespace', 'AWS/EC2')
        namespaces = namespace_param.split(',')  # Pass multiple namespaces as comma-separated list
        conn = self.get_connection(conn_type='cloudwatch')
        metrics = []

        # Fetch standard metrics by namespace(s)
        for metric in METRIC_TYPES:
            if metric['namespace'] in namespaces:
                metrics.append(dict(
                    name=metric['name'],
                    unit=metric['unit'],
                    label=METRIC_TITLE_MAPPING.get(metric['name'], metric['name']),
                    namespace=metric['namespace'],
                    nslabel='{0} {1}'.format(metric['namespace'].split('/')[1], _('metrics')).upper(),
                ))

        # Fetch custom metrics via list_metrics API call
        with boto_error_handler(self.request):
            list_metrics_result = conn.list_metrics(dimensions=dimensions)
            for metric in list_metrics_result:
                if not metric.namespace.startswith('AWS/'):
                    metrics.append(dict(
                        name=metric.name,
                        unit='None',  # Metric objects don't have a unit attr
                        label=metric.name,
                        namespace=metric.namespace,
                        nslabel='{0} {1}'.format(metric.namespace, _('metrics')).upper(),  # Namespace label
                    ))
                    if metric.namespace not in namespaces:
                        namespaces.append(metric.namespace)

        return dict(metrics=metrics, namespaces=namespaces)

    def get_items(self):
        conn = self.get_connection(conn_type='cloudwatch')
        return conn.list_metrics() if conn else []

    @staticmethod
    def get_url_for_resource(request, resource_type, resource_id):
        url = None
        if "LoadBalancerName" == resource_type:
            url = request.route_path('elb_view', id=resource_id)
        elif "VolumeId" == resource_type:
            url = request.route_path('volume_view', id=resource_id)
        elif "AutoScalingGroupName" == resource_type:
            url = request.route_path('scalinggroup_view', id=resource_id)
        elif "InstanceId" == resource_type:
            url = request.route_path('instance_view', id=resource_id)
        elif "ImageId" == resource_type:
            url = request.route_path('image_view', id=resource_id)
        return url
