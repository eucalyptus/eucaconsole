# -*- coding: utf-8 -*-
# Copyright 2013-2015 Hewlett Packard Enterprise Development LP
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
CloudWatch REST API

"""
from __future__ import division
from operator import itemgetter

import datetime
import json
import time

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from ..views import BaseView, boto_error_handler


CHART_COLORS = {
    0: '#1f77b4',
    1: '#822980',
    2: '#e6a818',
    3: '#8cc63e',
}

ISO8601 = '%Y-%m-%dT%H:%M:%S.%fZ'


class CloudWatchAPIMixin(object):
    @staticmethod
    def modify_granularity(duration):
        """
        Modify granularity based on duration to avoid exceeding 1440 data points

        :type duration: integer
        :param duration:  Length, in seconds, spanning the returned datapoints.

        :rtype: integer
        :returns: adusted granularity (period)

        """
        hour = 3600
        ranges = [  # min/max values are in hours
            dict(min=0, max=6, period=300),  # Set granularity to 5 minutes if duration < 6 hours
            dict(min=6, max=12, period=600),
            dict(min=12, max=24, period=1200),
            dict(min=24, max=3 * 24, period=1 * hour),
            dict(min=3 * 24, max=7 * 24, period=3 * hour),
            dict(min=7 * 24, max=30 * 24, period=6 * hour),
        ]
        for item in ranges:
            if (item.get('min') * hour) <= duration < (item.get('max') * hour):
                return item.get('period')
        return 300  # Default to 5 minutes

    @staticmethod
    def collapse_metrics(unit, statistic, divider=1, stats=None):
        # Collapse to MB when appropriate
        max_value = max(stat.get(statistic) for stat in stats) if stats else 0
        kb = 1024
        if max_value > 10 ** 4:
            divider = kb
            unit = 'Kilobytes'
        if max_value > 10 ** 7:
            divider = kb ** 2
            unit = 'Megabytes'
            if max_value > 10 ** 10:
                divider = kb ** 3
                unit = 'Gigabytes'
        return unit, divider

    @staticmethod
    def get_volume_metric_modifier(metric, statistic, period, default_unit=None):
        """
        :param metric: e.g. 'VolumeReadBytes'
        :param statistic: e.g. 'Average'
        :param period: granularity (in seconds)
        :param default_unit:
        :return: unit, divider, multiplier
        :rtype: tuple

        NOTES
        - The divider values don't exactly match the divider/multiplier approach documented at
          http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-volume-status.html
          since the order of operations are a bit different here
          (e.g. Read/write bandwidth divider is 1024 * period rather than 1024 / period)
        - For the average latency and average size graphs, the average is calculated over the total
          number of operations that completed during the period.

        """
        if metric in ['VolumeReadBytes', 'VolumeWriteBytes']:
            if statistic == 'Sum':  # Read/write bandwidth
                return 'KiB/sec', 1024 * period, 1
            elif statistic == 'Average':  # Avg read/write size
                divider = 1024
                return 'KiB/op', divider, 1
        if metric in ['VolumeReadOps', 'VolumeWriteOps']:  # Read/write throughput
            return 'Ops/sec', period, 1
        if metric == 'VolumeIdleTime':  # Percent time spent idle
            return 'Percent', period / 100, 1
        if metric in ['VolumeTotalReadTime', 'VolumeTotalWriteTime']:  # Avg read/write latency
            return 'ms/op', 1, 1000
        return default_unit, 1, 1

    @staticmethod
    def get_cloudwatch_stats(cw_conn=None, period=60, duration=600, metric='CPUUtilization', namespace='AWS/EC2',
                             statistic='Average', idtype='InstanceId', ids=None, unit=None, dimensions=None,
                             start_time=None, end_time=None):
        """
        Wrapper for time-series data for statistics of a given metric for one or more resources

        :param cw_conn: Boto CloudWatch connection object

        :type period: integer
        :param period: The granularity, in seconds, of the returned datapoints; must be a multiple of 60

        :type duration: integer
        :param duration:  Length, in seconds, spanning the returned datapoints.
        Example: duration=3600 returns the last hour's data

        :type metric: str
        :param metric: Metric name, see eucaconsole.constants.cloudwatch.METRIC_TYPES

        :type namespace: str
        :param namespace: Either 'AWS/EC2', 'AWS/EBS', or 'AWS/AutoScaling'

        :type statistic: str
        :param statistic: Valid values: Average | Sum | SampleCount | Maximum | Minimum

        :type idtype: str
        :param idtype: Dimension key (e.g. 'InstanceId', 'ImageId')

        :type ids: list
        :param ids: List of resource ids

        :type unit: str
        :param unit: Valid values are Seconds, Kilobytes, Percent, Count, Kilobytes/Second, Count/Second, et. al.

        :type dimensions: dict
        :param dimensions: dict of dimension/value mapping (e.g. {'AvailabilityZone': 'us-west-2a'})

        :type start_time: datetime
        :param start_time: supply a start time to override duration relative to now

        :type end_time: datetime
        :param end_time: supply a start time to override duration relative to now

        """
        if start_time and end_time:
            start_time = datetime.datetime.strptime(start_time, ISO8601)
            end_time = datetime.datetime.strptime(end_time, ISO8601)
        else:
            end_time = datetime.datetime.utcnow()
            start_time = end_time - datetime.timedelta(seconds=duration)
        statistics = [statistic]
        base_dimensions = {idtype: ids} if idtype and ids else {}
        if dimensions:
            base_dimensions.update(dimensions)
        try:
            return cw_conn.get_metric_statistics(
                period, start_time, end_time, metric, namespace, statistics,
                dimensions=base_dimensions, unit=unit
            )
        except NotImplementedError:
            # TODO: Remove try/except block when moto has implemented cw_conn.get_metric_statistics
            return None


class CloudWatchAPIView(BaseView, CloudWatchAPIMixin):
    """CloudWatch Charts API"""

    def __init__(self, request):
        super(CloudWatchAPIView, self).__init__(request)
        self.request = request
        self.cw_conn = self.get_connection(conn_type='cloudwatch')
        self.metric = self.request.params.get('metric') or 'CPUUtilization'
        self.namespace = self.request.params.get('namespace', 'AWS/EC2')
        self.statistic = self.request.params.get('statistic') or 'Average'
        self.zones = self.request.params.get('zones')
        self.split_zone_metrics = ['HealthyHostCount', 'UnHealthyHostCount']
        self.idtype = self.request.params.get('idtype')
        self.ids = self.request.params.get('ids')
        self.dimensions = self.request.params.get('dimensions')
        self.unit = self.request.params.get('unit')
        self.duration = int(self.request.params.get('duration', 3600))
        self.start_time = self.request.params.get('startTime', None)
        self.end_time = self.request.params.get('endTime', None)
        self.tz_offset = int(self.request.params.get('tzoffset', 0))
        self.collapse_to_kb_mb_gb = [
            'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskWriteBytes', 'VolumeReadBytes', 'VolumeWriteBytes'
        ]
        self.expand_to_ms = ['Latency', 'VolumeTotalReadTime']

    @view_config(route_name='cloudwatch_api', renderer='json', request_method='GET')
    def cloudwatch_api(self):
        """
        REST API endpoint for fetching time-series cloudwatch data

        Examples...
        Fetch average CPU utilization percentage for instance 'i-foo' for the past hour
        /cloudwatch/api?ids=i-foo&idtype=InstanceId&metric=CPUUtilization&duration=3600&unit=Percent&statistic=Average

        """
        stats_list = []
        unit = self.unit
        max_value = 0

        if self.dimensions:
            lines = json.loads(self.dimensions)
            if len(lines) > 1:
                for idx, line in enumerate(lines):
                    unit, stats_series, max_value = self.get_stats_series(line['dimensions'], line['label'])
                    if stats_series.get('values'):
                        if CHART_COLORS.get(idx):
                            # Use custom line colors
                            stats_series['color'] = CHART_COLORS.get(idx)
                        stats_list.append(stats_series)
            else:
                line = lines[0]
                unit, stats_series, max_value = self.get_stats_series(line['dimensions'], line['label'])
                stats_list.append(stats_series)
        else:
            if self.zones and len(self.zones.split(',')) > 1:
                for idx, zone in enumerate(self.zones.split(',')):
                    dimensions = {'AvailabilityZone': zone}
                    unit, stats_series, max_value = self.get_stats_series(dimensions)
                    if stats_series.get('values'):
                        if CHART_COLORS.get(idx):
                            # Use custom line colors
                            stats_series['color'] = CHART_COLORS.get(idx)
                        stats_list.append(stats_series)
            else:
                unit, stats_series, max_value = self.get_stats_series()
                stats_list.append(stats_series)

        return dict(
            unit=unit,
            results=stats_list,
            max_value=max_value,
        )

    def get_stats_series(self, dimensions=None, label=None):
        multiplier = 1
        divider = 1
        unit = self.unit
        period = int(self.request.params.get('period', 300))
        if period % 60 != 0:
            raise HTTPBadRequest()  # Period (granularity) must be a multiple of 60 seconds

        # Allow ids to be passed as a comma-separated list
        ids = None
        if self.ids:
            ids = self.ids.split(',')

        adjust_granularity = int(self.request.params.get('adjustGranularity', 1))
        if adjust_granularity:
            period = self.modify_granularity(self.duration)
        with boto_error_handler(self.request):
            stats = self.get_cloudwatch_stats(
                self.cw_conn, period, self.duration, self.metric, self.namespace,
                self.statistic, self.idtype, ids, self.unit, dimensions, self.start_time, self.end_time)

        if self.metric in self.collapse_to_kb_mb_gb:
            unit, divider = self.collapse_metrics(self.unit, self.statistic, divider, stats)

        if self.metric in self.expand_to_ms:
            multiplier, unit = 1000, 'Milliseconds'

        if self.metric.startswith('Volume'):
            unit, divider, multiplier = self.get_volume_metric_modifier(
                self.metric, self.statistic, period, unit)

        # Display 'Count' rather than 'None' as unit for Auto Scaling metrics
        if unit == 'None' and self.namespace == 'AWS/AutoScaling':
            unit = 'Count'

        json_stats = self.get_json_stats(self.statistic, stats, divider, multiplier)
        max_value = max(val.get('y') for val in json_stats) if json_stats else 0
        key = self.metric
        if dimensions and dimensions.values():
            if label:
                key = label
            else:
                key = dimensions.values()[0]
        series = dict(key=key, values=json_stats)
        return unit, series, max_value

    def get_json_stats(self, statistic=None, stats=None, divider=1, multiplier=1):
        json_stats = []
        for stat in stats:
            amount = stat.get(statistic)
            if divider != 1:
                amount = float(amount) / divider
            if multiplier != 1:
                amount *= multiplier
            dt_object = stat.get('Timestamp')
            if self.tz_offset:  # Convert to local time based on client offset
                dt_object = dt_object - datetime.timedelta(minutes=self.tz_offset)
            json_stats.append(dict(
                # Note: time.mktime must be inline here to avoid chart tick formatting issues
                x=time.mktime(dt_object.timetuple()) * 1000,  # Milliseconds since Unix epoch
                y=amount
            ))
        # Sort by timestamp to avoid chart anomalies
        return sorted(json_stats, key=itemgetter('x'))
