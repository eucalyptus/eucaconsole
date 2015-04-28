# -*- coding: utf-8 -*-
# Copyright 2013-2014 Eucalyptus Systems, Inc.
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
import time

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from ..views import BaseView, boto_error_handler


class CloudWatchAPIMixin(object):
    @staticmethod
    def adjust_granularity(duration):
        """
        Adjust granularity based on duration to avoid exceeding 1440 data points

        :type duration: integer
        :param duration:  Length, in seconds, spanning the returned datapoints.

        :rtype: integer
        :returns: adusted granularity (period)

        """
        hour = 3600
        ranges = [  # min/max values are in hours
            dict(min=0, max=6, period=300),  # Set granularity to 5 minutes if duration < 6 hours
            dict(min=6, max=24, period=600),
            dict(min=24, max=3 * 24, period=1 * hour),
            dict(min=3 * 24, max=7 * 24, period=3 * hour),
            dict(min=7 * 24, max=30 * 24, period=6 * hour),
        ]
        for item in ranges:
            if (item.get('min') * hour) <= duration < (item.get('max') * hour):
                return item.get('period')

        return 300  # Default to 5 minutes


class CloudWatchAPIView(BaseView, CloudWatchAPIMixin):
    """CloudWatch Charts API"""

    def __init__(self, request):
        super(CloudWatchAPIView, self).__init__(request)
        self.request = request
        self.cw_conn = self.get_connection(conn_type='cloudwatch')

    @view_config(route_name='cloudwatch_api', renderer='json')
    def cloudwatch_api(self):
        """
        REST API endpoint for fetching time-series cloudwatch data

        Examples...
        Fetch average CPU utilization percentage for instance 'i-foo' for the past hour
        /cloudwatch/api?ids=i-foo&idtype=InstanceId&metric=CPUUtilization&duration=3600&unit=Percent&statistic=Average

        """
        ids = self.request.params.get('ids')
        if not ids:
            raise HTTPBadRequest()
        ids = ids.split(',')  # Allow ids to be passed as a comma-separated list

        period = int(self.request.params.get('period', 300))
        if period % 60 != 0:
            raise HTTPBadRequest()  # Period (granularity) must be a multiple of 60 seconds

        duration = int(self.request.params.get('duration', 3600))
        adjust_granularity = int(self.request.params.get('adjustGranularity', 1))
        if adjust_granularity:
            period = self.adjust_granularity(duration)
        metric = self.request.params.get('metric') or 'CPUUtilization'
        namespace = u'AWS/{0}'.format(self.request.params.get('namespace', 'EC2'))
        statistic = self.request.params.get('statistic') or 'Average'
        idtype = self.request.params.get('idtype') or 'InstanceId'
        tz_offset = int(self.request.params.get('tzoffset', 0))
        unit = self.request.params.get('unit')
        convert_to_kilobytes = ['NetworkIn', 'NetworkOut']
        json_stats = []
        divider = 1

        with boto_error_handler(self.request):
            stats = self.get_stats(period, duration, metric, namespace, statistic, idtype, ids, unit)

        if metric in convert_to_kilobytes:
            divider = 1000
            unit = 'Kilobytes'

        for stat in stats:
            amount = stat.get(statistic)
            if divider != 1:
                amount /= divider
            dt_object = stat.get('Timestamp')
            if tz_offset:  # Convert to local time based on client offset
                dt_object = dt_object - datetime.timedelta(minutes=tz_offset)
            json_stats.append(dict(
                # Note: time.mktime must be inline here to avoid chart tick formatting issues
                x=time.mktime(dt_object.timetuple()) * 1000,  # Milliseconds since Unix epoch
                y=amount
            ))

        # Sort by timestamp to avoid chart anomalies
        json_stats = sorted(json_stats, key=itemgetter('x'))

        return dict(
            unit=unit,
            results=[dict(key=metric, values=json_stats)],
        )

    def get_stats(self, period=60, duration=600, metric='CPUUtilization', namespace='AWS/EC2',
                  statistic='Average', idtype='InstanceId', ids=None, unit=None):
        """
        Wrapper for time-series data for statistics of a given metric for one or more resources

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

        """
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(seconds=duration)
        statistics = [statistic]

        return self.cw_conn.get_metric_statistics(
            period, start_time, end_time, metric, namespace, statistics,
            dimensions={idtype: ids}, unit=unit
        )
