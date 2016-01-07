# -*- coding: utf-8 -*-
# Copyright 2015-2016 Hewlett Packard Enterprise Development LP
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
import simplejson as json

from pyramid.view import view_config

from ..constants.cloudwatch import (
    MONITORING_DURATION_CHOICES, METRIC_TITLE_MAPPING, STATISTIC_CHOICES, GRANULARITY_CHOICES,
    DURATION_GRANULARITY_CHOICES_MAPPING, METRIC_TYPES
)
from ..i18n import _
from ..views import LandingPageView, BaseView
from . import boto_error_handler


class CloudWatchMetricsView(LandingPageView):
    """CloudWatch Metrics landing page view"""
    TEMPLATE = '../templates/cloudwatch/metrics.pt'

    def __init__(self, request):
        super(CloudWatchMetricsView, self).__init__(request)
        self.title_parts = [_(u'Metrics')]
        self.initial_sort_key = 'name'
        self.prefix = '/cloudwatch/metrics'
        self.cloudwatch_conn = self.get_connection(conn_type='cloudwatch')
        self.filter_keys = ['name']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name')),
        ]
        search_facets = [
            {'name': 'metric_name', 'label': _(u"Metric name"), 'options': []},
            {'name': 'res_ids', 'label': _(u"Resource"), 'options': []},
            {'name': 'res_types', 'label': _(u"Resource type"), 'options': []}
        ]
        self.render_dict = dict(
            filter_keys=self.filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.request.route_path('cloudwatch_metrics_json'),
            statistic_choices=STATISTIC_CHOICES,
            duration_choices=MONITORING_DURATION_CHOICES,
            chart_options_json=self.get_chart_options_json()
        )

    @view_config(route_name='cloudwatch_metrics', renderer=TEMPLATE, request_method='GET')
    def metrics_landing(self):
        return self.render_dict

    def get_chart_options_json(self):
        return BaseView.escape_json(json.dumps({
            'metric_title_mapping': METRIC_TITLE_MAPPING,
            'granularity_choices': GRANULARITY_CHOICES,
            'duration_granularities_mapping': DURATION_GRANULARITY_CHOICES_MAPPING,
            'largeChart': True
        }))


class CloudWatchMetricsJsonView(BaseView):
    """JSON response for CloudWatch Metrics landing page et. al."""
    @view_config(route_name='cloudwatch_metrics_json', renderer='json', request_method='POST')
    def cloudwatch_metrics_json(self):
        categories = [
            dict(
                name='scalinggroup',
                label=_(u'Auto scaling groups'),
                namespace='AWS/AutoScaling',
            ),
            dict(
                name='ebs',
                label=_(u'Elastic Block Storage'),
                namespace='AWS/EBS',
            ),
            dict(
                name='ec2',
                label=_(u'Elastic Compute Cloud'),
                namespace='AWS/EC2',
            ),
            dict(
                name='elb',
                label=_(u'Elastic Load Balancing'),
                namespace='AWS/ELB',
            ),
        ]
        with boto_error_handler(self.request):
            items = self.get_items()
            metrics = []
            for cat in categories:
                namespace = cat['namespace']
                tmp = [{
                    'name': item.name,
                    'namespace': item.namespace,
                    'dimensions': item.dimensions
                } for item in items if item.namespace == namespace and item.dimensions]
                tmp = [(met['dimensions'].items(), met['name']) for met in tmp]
                cat_metrics = []
                for metric in tmp:
                    metric_dims = metric[0]
                    unit = [mt['unit'] for mt in METRIC_TYPES if mt['name'] == metric[1]]
                    cat_metrics.append(dict(
                        cat_name=cat['name'],
                        cat_label=cat['label'],
                        namespace=cat['namespace'],
                        unique_id=metric[1] + '-' + '-'.join([dim[1][0] for dim in metric_dims]),
                        resources=[dict(
                            res_id=dim[1][0],
                            res_type=dim[0],
                            res_url=self.get_url_for_resource(self.request, dim[0], dim[1][0])
                        ) for dim in metric_dims],
                        res_ids=[dim[1][0] for dim in metric_dims],
                        res_types=[dim[0] for dim in metric_dims],
                        unit=unit[0] if unit else '',
                        metric_name=metric[1]
                    ))
                metrics.extend(cat_metrics)

            # import logging; logging.info(json.dumps(metrics, indent=2))
            return dict(results=metrics)

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

