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

from ..i18n import _


SCALING_GROUP_EMPTY_DATA_MESSAGE = _('No data available for this scaling group.')
SCALING_GROUP_MONITORING_CHARTS_LIST = (
    {
        'metric': 'GroupTotalInstances', 'unit': 'None', 'statistic': 'Maximum', 'namespace': 'AutoScaling',
        'empty_msg': SCALING_GROUP_EMPTY_DATA_MESSAGE, 'title': _(u'Total instances'),
        'help': _('The total number of instances in the Auto Scaling group.  Identifies the number of instances '
                  'that are in service, pending, and terminating.'),
    },
    {
        'metric': 'GroupInServiceInstances', 'unit': 'None', 'statistic': 'Maximum', 'namespace': 'AutoScaling',
        'empty_msg': SCALING_GROUP_EMPTY_DATA_MESSAGE, 'title': _(u'In service instances'),
        'help': _('The number of instances that are running as part of the Auto Scaling group.  '
                  'Does not include instances that are pending or terminating.'),
    },
    {
        'metric': 'GroupMinSize', 'unit': 'None', 'statistic': 'Maximum', 'namespace': 'AutoScaling',
        'empty_msg': SCALING_GROUP_EMPTY_DATA_MESSAGE, 'title': _(u'Group min size'),
        'help': _('The minimum size of the Auto Scaling group.'),
    },
    {
        'metric': 'GroupMaxSize', 'unit': 'None', 'statistic': 'Maximum', 'namespace': 'AutoScaling',
        'empty_msg': SCALING_GROUP_EMPTY_DATA_MESSAGE, 'title': _(u'Group max size'),
        'help': _('The maximum size of the Auto Scaling group.'),
    },
    {
        'metric': 'GroupDesiredCapacity', 'unit': 'None', 'statistic': 'Maximum', 'namespace': 'AutoScaling',
        'empty_msg': SCALING_GROUP_EMPTY_DATA_MESSAGE, 'title': _(u'Group desired capacity'),
        'help': _('The number of instances that the Auto Scaling group attempts to maintain.'),
    },
    {
        'metric': 'GroupPendingInstances', 'unit': 'None', 'statistic': 'Maximum', 'namespace': 'AutoScaling',
        'empty_msg': SCALING_GROUP_EMPTY_DATA_MESSAGE, 'title': _(u'Pending instances'),
        'help': _('The number of instances that are pending. A pending instance is not yet in service. '
                  'This metric does not include instances that are in service or terminating.'),
    },
    {
        'metric': 'GroupTerminatingInstances', 'unit': 'None', 'statistic': 'Maximum', 'namespace': 'AutoScaling',
        'empty_msg': SCALING_GROUP_EMPTY_DATA_MESSAGE, 'title': _(u'Terminating instances'),
        'help': _('The number of instances that are in the process of terminating. '
                  'This metric does not include instances that are in service or pending.'),
    },
    # TODO: Uncomment when Eucalyptus supports Standby Instances
    # {
    #     'metric': 'GroupStandbyInstances', 'unit': 'None', 'statistic': 'Maximum', 'namespace': 'AutoScaling',
    #     'empty_msg': SCALING_GROUP_EMPTY_DATA_MESSAGE, 'title': _(u'Standby instances'),
    #     'help': _('The number of instances that are in a Standby state. '
    #               'Instances in this state are still running but are not actively in service.'),
    # },
)

INSTANCE_EMPTY_DATA_MESSAGE = _('No data available for instances in the scaling group.')
SCALING_GROUP_INSTANCE_MONITORING_CHARTS_LIST = (
    {
        'metric': 'CPUUtilization', 'unit': 'Percent', 'statistic': 'Average', 'namespace': 'EC2',
        'empty_msg': INSTANCE_EMPTY_DATA_MESSAGE, 'title': _(u'CPU utilization %'),
        'help': _('The average CPU utilization % for instances in the scaling group.'),
    },
    {
        'metric': 'DiskReadBytes', 'unit': 'Bytes', 'statistic': 'Average', 'namespace': 'EC2',
        'empty_msg': INSTANCE_EMPTY_DATA_MESSAGE, 'title': _(u'Disk read data'),
        'help': _('The average disk read data for instances in the scaling group.'),
    },
    {
        'metric': 'DiskReadOps', 'unit': 'Count', 'statistic': 'Average', 'namespace': 'EC2',
        'empty_msg': INSTANCE_EMPTY_DATA_MESSAGE, 'title': _(u'Disk read operations'),
        'help': _('The average disk read operations for instances in the scaling group.'),
    },
    {
        'metric': 'DiskWriteBytes', 'unit': 'Bytes', 'statistic': 'Average', 'namespace': 'EC2',
        'empty_msg': INSTANCE_EMPTY_DATA_MESSAGE, 'title': _(u'Disk write data'),
        'help': _('The average disk write data for instances in the scaling group.'),
    },
    {
        'metric': 'DiskWriteOps', 'unit': 'Count', 'statistic': 'Average', 'namespace': 'EC2',
        'empty_msg': INSTANCE_EMPTY_DATA_MESSAGE, 'title': _(u'Disk write operations'),
        'help': _('The average disk write operations for instances in the scaling group.'),
    },
    {
        'metric': 'NetworkIn', 'unit': 'Bytes', 'statistic': 'Average', 'namespace': 'EC2',
        'empty_msg': INSTANCE_EMPTY_DATA_MESSAGE, 'title': _(u'Network in'),
        'help': _('The average incoming network bandwidth for instances in the scaling group.'),
    },
    {
        'metric': 'NetworkOut', 'unit': 'Bytes', 'statistic': 'Average', 'namespace': 'EC2',
        'empty_msg': INSTANCE_EMPTY_DATA_MESSAGE, 'title': _(u'Network out'),
        'help': _('The average outgoing network bandwidth for instances in the scaling group.'),
    },
)
