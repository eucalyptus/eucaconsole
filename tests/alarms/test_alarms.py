# Copyright 2013-2016 Hewlett Packard Enterprise Development LP
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

import unittest

import boto

from boto.ec2.cloudwatch import MetricAlarm
from moto import mock_cloudwatch

from eucaconsole.models.alarms import Alarm


class MockAlarmMixin(object):
    @staticmethod
    @mock_cloudwatch
    def make_alarm(name='test-alarm', metric='CPUUtilization', namespace='AWS/EC2', statistic='Average',
                   comparison='>=', threshold=90, period=500, evaluation_periods=1, unit='Percent',
                   description='Test Alarm', dimensions=None):
        if dimensions is None:
            dimensions = {}
        cw_conn = boto.connect_cloudwatch('us-east')
        metric_alarm = MetricAlarm(
            name=name, metric=metric, namespace=namespace, statistic=statistic, comparison=comparison,
            threshold=threshold, period=period, evaluation_periods=evaluation_periods, unit=unit,
            description=description, dimensions=dimensions
        )
        alarm = cw_conn.put_metric_alarm(metric_alarm)
        return cw_conn, alarm


class ResourceAlarmsTestCase(unittest.TestCase, MockAlarmMixin):
    @mock_cloudwatch
    def test_fetch_alarms_for_instance(self):
        instance_id = 'i-123456'
        cw_conn, alarm_created = self.make_alarm(dimensions={'InstanceId': [instance_id]})
        instance_alarms = Alarm.get_alarms_for_resource(instance_id, dimension_key='InstanceId', cw_conn=cw_conn)
        self.assertEqual(len(instance_alarms), 1)

    @mock_cloudwatch
    def test_fetch_alarms_for_unknown_instance(self):
        instance_id = 'i-123456'
        cw_conn, alarm_created = self.make_alarm(dimensions={'InstanceId': [instance_id]})
        instance_alarms = Alarm.get_alarms_for_resource('unlikely-id', dimension_key='InstanceId', cw_conn=cw_conn)
        self.assertEqual(len(instance_alarms), 0)

    @mock_cloudwatch
    def test_fetch_alarms_for_load_balancer(self):
        elb_name = 'test_elb'
        alarm_kwargs = dict(
            metric='RequestCount', namespace='AWS/ELB', statistic='Sum', unit=None,
            dimensions={'LoadBalancerName': elb_name},
        )
        cw_conn, alarm_created = self.make_alarm(**alarm_kwargs)
        elb_alarms = Alarm.get_alarms_for_resource(elb_name, dimension_key='LoadBalancerName', cw_conn=cw_conn)
        self.assertEqual(len(elb_alarms), 1)
