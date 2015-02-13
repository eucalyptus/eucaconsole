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
import datetime

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from ..views import BaseView


class CloudWatchAPIView(BaseView):
    def __init__(self, request):
        super(CloudWatchAPIView, self).__init__(request)
        self.request = request
        self.cw_conn = self.get_connection(conn_type='cloudwatch')

    @view_config(route_name='cloudwatch_api', renderer='json')
    def cloudwatch_api(self):
        """
        REST API endpoint for fetching time-series cloudwatch data

        Examples...
        Fetch CPUUtilization percentage for instance 'i-foobar' for the past hour:
          /cloudwatch/api?ids=i-foobar&duration=3600&unit=Percent

        """
        ids = self.request.params.get('ids')
        if not ids:
            raise HTTPBadRequest()
        ids = ids.split(',')  # Allow ids to be passed as a comma-separated list
        period = int(self.request.params.get('period', 60))
        if period % 60 != 0:
            raise HTTPBadRequest()  # Period (granularity) must be a multiple of 60 seconds
        duration = int(self.request.params.get('duration', 600))
        metric = self.request.params.get('metric', 'CPUUtilization')
        namespace = u'AWS/{0}'.format(self.request.params.get('namespace', 'EC2'))
        statistic = self.request.params.get('statistic', 'Average')
        idtype = self.request.params.get('idtype', 'InstanceId')
        unit = self.request.params.get('unit')
        stats = self.get_stats(period, duration, metric, namespace, statistic, idtype, ids, unit)
        json_stats = []
        for stat in stats:
            json_stats.append(dict(
                timestamp=stat.get('Timestamp').isoformat(),
                statistic=stat.get(statistic),
            ))
        return dict(unit=unit, results=json_stats)

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
