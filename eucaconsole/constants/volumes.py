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


VOLUME_EMPTY_DATA_MESSAGE = _('No data available for this volume.')
VOLUME_MONITORING_CHARTS_LIST = [
    {
        'metric': 'VolumeReadBytes', 'unit': 'Bytes', 'statistic': 'Sum',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Read bandwidth'),
        'help': _('Read bandwith, computed using the following: Sum(VolumeReadBytes) / Period'),
    },
    {
        'metric': 'VolumeWriteBytes', 'unit': 'Bytes', 'statistic': 'Sum',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Write bandwidth'),
        'help': _('Write bandwith, computed using the following: Sum(VolumeWriteBytes) / Period'),
    },
    {
        'metric': 'VolumeReadOps', 'unit': 'Count', 'statistic': 'Sum',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Read throughput (Ops/sec)'),
        'help': _('Read operations per second, computed using the following: Sum(VolumeReadOps) / Period'),
    },
    {
        'metric': 'VolumeWriteOps', 'unit': 'Count', 'statistic': 'Sum',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Write throughput (Ops/sec)'),
        'help': _('Write operations per second, computed using the following: Sum(VolumeWriteOps) / Period'),
    },
    {
        'metric': 'VolumeQueueLength', 'unit': 'Count', 'statistic': 'Average',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Average queue length (ops)'),
        'help': _('Average number of read and write operation requests waiting to be completed '
                  'in a specified period time.  Computed using the following: Avg(VolumeQueueLength)'),
    },
    {
        'metric': 'VolumeIdleTime', 'unit': 'Seconds', 'statistic': 'Sum',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Percent time spent idle'),
        'help': _('Percentage of time in a specified period when no read or write operations were submitted.'
                  'Computed using the following: Sum(VolumeIdleTime) / Period * 100'),
    },
    {
        'metric': 'VolumeReadBytes', 'unit': 'Bytes', 'statistic': 'Average',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Average read size (KiB/op)'),
        'help': _('Average read size in kilobytes, computed using the following: Avg(VolumeReadBytes) / 1024'),
    },
    {
        'metric': 'VolumeWriteBytes', 'unit': 'Bytes', 'statistic': 'Average',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Average write size (KiB/op)'),
        'help': _('Average write size in kilobytes, computed using the following: Avg(VolumeWriteBytes) / 1024'),
    },
    {
        'metric': 'VolumeTotalReadTime', 'unit': 'Seconds', 'statistic': 'Average',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Average read latency (ms/op)'),
        'help': _('Average read time in milliseconds, computed using the following: Avg(VolumeTotalReadTime) * 1000'),
    },
    {
        'metric': 'VolumeTotalWriteTime', 'unit': 'Seconds', 'statistic': 'Average',
        'empty_msg': VOLUME_EMPTY_DATA_MESSAGE, 'title': _(u'Average write latency (ms/op)'),
        'help': _('Average write time in milliseonds, computed using the following: Avg(VolumeTotalWriteTime) * 1000'),
    },
]
