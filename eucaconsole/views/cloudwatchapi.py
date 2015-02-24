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

import datetime
import time

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from ..views import BaseView, boto_error_handler


class CloudWatchAPIView(BaseView):
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
        period = int(self.request.params.get('period', 60))
        if period % 60 != 0:
            raise HTTPBadRequest()  # Period (granularity) must be a multiple of 60 seconds
        duration = int(self.request.params.get('duration', 3600))
        metric = self.request.params.get('metric') or 'CPUUtilization'
        namespace = u'AWS/{0}'.format(self.request.params.get('namespace', 'EC2'))
        statistic = self.request.params.get('statistic') or 'Average'
        idtype = self.request.params.get('idtype') or 'InstanceId'
        tz_offset = int(self.request.params.get('tzoffset', 0))
        unit = self.request.params.get('unit')
        with boto_error_handler(self.request):
            stats = self.get_stats(period, duration, metric, namespace, statistic, idtype, ids, unit)
        json_stats = []
        divider = 1
        if unit == 'Bytes':  # Convert Bytes to Kilobytes
            divider = 1000
            unit = 'Kilobytes'
        for stat in stats:
            amount = stat.get(statistic)
            if divider != 1:
                amount /= divider
            dt_object = stat.get('Timestamp')
            if tz_offset:  # Convert to local time based on client offset
                dt_object = dt_object - datetime.timedelta(minutes=tz_offset)
            timestamp = time.mktime(dt_object.timetuple()) * 1000,  # Milliseconds since Unix epoch
            json_stats.append(dict(x=timestamp, y=amount))
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
        # TODO: Accept start/end time params, falling back to duration if missing
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(seconds=duration)
        statistics = [statistic]
        return self.cw_conn.get_metric_statistics(
            period, start_time, end_time, metric, namespace, statistics,
            dimensions={idtype: ids}, unit=unit
        )
