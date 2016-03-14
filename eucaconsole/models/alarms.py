# -*- coding: utf-8 -*-
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

from itertools import chain

from ..i18n import _


class Alarm(object):

    @staticmethod
    def get_alarms_for_resource(resource_id, dimension_key=None, cw_conn=None, alarms=None):
        """
        Fetch alarms for a resource by resource id. Fetches alarms if not passed as a list.

        :param resource_id: ID of resource (e.g. 'i-123456' for an EC2 instance)
        :param dimension_key: CloudWatch dimension (e.g. 'InstanceId' for EC2 instances)
        :param cw_conn: CloudWatch connection object
        :param alarms: list of (ideally pre-filtered) alarms
        :return: de-duped list of alarms for the given resource

        Example Use Cases:
        1. Fetch alarms for a given instance, passing a pre-filtered set of alarms, on the instances landing page...
           alarms = alarms = [alarm for alarm in cw_conn.describe_alarms() if 'InstanceId' in alarm.dimensions]
           instance_foo_alarms = get_alarms_for_resource('i-foo', alarms=alarms)

        2. Fetch alarms for an instance on the instance monitoring page (allowing alarms to be fetched inline)
           instance_bar_alarms = get_alarms_for_resource('i-bar', dimension_key='InstanceId', cw_conn=cw_conn)

        """
        if alarms is None and dimension_key is not None:
            alarms = [alarm for alarm in cw_conn.describe_alarms() if dimension_key in alarm.dimensions]
        return set([alarm for alarm in alarms if resource_id in chain.from_iterable(alarm.dimensions.values())])

    @classmethod
    def get_resource_alarm_status(cls, resource_id, alarms):
        """ Get alarm status for a given resource
            Return 'Alarm' if at least one alarm is in ALARM state
            Fall back to 'Insufficient data' if at least one is insufficient and none are in ALARM state
            Return OK only if all alarms are in that state

        :param alarms: list of Alarm objects
        :param resource_id: resource id or name (e.g. 'i-123456' for an EC2 instance)
        :returns: Alarm status
        :rtype: str

        """
        resource_alarms = cls.get_alarms_for_resource(resource_id, alarms=alarms)
        alarm_states = set([alarm.state_value for alarm in resource_alarms])
        if alarm_states:
            if 'ALARM' in alarm_states:
                return _(u'Alarm')
            elif 'INSUFFICIENT_DATA' in alarm_states:
                return _(u'Insufficient data')
            else:
                return _(u'OK')
        return ''  # Default to when resource has no alarms set

