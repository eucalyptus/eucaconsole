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
        period = int(self.request.params.get('period', 60))
        duration = int(self.request.params.get('duration', 600))
        metric = self.request.params.get('metric', 'CPUUtilization')
        namespace = self.request.params.get('namespace', 'AWS/EC2')
        statistic = self.request.params.get('statistic', 'Average')
        idtype = self.request.params.get('idtype', 'InstanceId')
        ids = self.request.params.get('ids')
        return dict(
            results=self.get_stats(period, duration, metric, namespace, statistic, idtype, ids)
        )

    def get_stats(self, period=60, duration=600, metric='CPUUtilization', namespace='AWS/EC2',
                  statistic='Average', idtype='InstanceId', ids=None):
        """
        Wrapper for time-series data for statistics of a given metric for one or more resources
        Notes:
         - Duration is the stats to display for the last _____ seconds
         - Pass ids as a comma-separated list (w/o spaces)
        """
        ids = ids.split(',') if ids else []
        if not ids:
            raise HTTPBadRequest()
        now = datetime.datetime.now()
        start_time = now - datetime.timedelta(seconds=duration)
        end_time = now
        statistics = [statistic]
        self.cw_conn.get_metric_statistics(
            period, start_time, end_time, metric, namespace, statistics,
            dimensions={idtype: ids}
        )
