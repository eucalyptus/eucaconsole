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
Eucalyptus and AWS Instance constants

"""

# TODO: Confirm we have the most recent list of choices here
AWS_INSTANCE_TYPE_CHOICES = [
    ('t2.micro', 't2.micro (1 vCPU, 6 CPU credits/hour, 1 GiB memory, EBS-Only)'),
    ('t2.small', 't2.small (1 vCPU, 12 CPU credits/hour, 2 GiB memory, EBS-Only)'),
    ('t2.medium', 't2.medium (2 vCPU, 24 CPU credits/hour, 4 GiB memory, EBS-Only)'),
    ('t2.large', 't2.large (2 vCPU, 36 CPU credits/hour, 8 GiB memory, EBS-Only)'),
    ('m4.large', 'm4.large (2 vCPUs, 8 GiB memory, EBS-Only)'),
    ('m4.xlarge', 'm4.xlarge (4 vCPUs, 16 GiB memory, EBS-Only)'),
    ('m4.2xlarge', 'm4.2xlarge (8 vCPUs, 32 GiB memory, EBS-Only)'),
    ('m4.4xlarge', 'm4.4xlarge (16 vCPUs, 64 GiB memory, EBS-Only)'),
    ('m4.10xlarge', 'm4.10xlarge (40 vCPUs, 160 GiB memory, EBS-Only)'),
    ('m3.medium', ' m3.medium (1 vCPU, 3.75 GiB memory, 1 x 4 GiB SSD Storage Capacity)'),
    ('m3.large', ' m3.large (2 vCPUs, 7.5 GiB memory, 1 x 32 GiB SSD Storage Capacity)'),
    ('m3.xlarge', ' m3.xlarge (4 vCPUs, 15 GiB memory, 2 x 40 GiB SSD Storage Capacity)'),
    ('m3.2xlarge', 'm3.2xlarge (8 vCPUs, 30 GiB memory, 2 x 80 GiB SSD Storage Capacity)'),
    ('c4.large', 'c4.large (2 vCPUs, 3.75 GiB memory, EBS Only)'),
    ('c4.xlarge', 'c4.xlarge (4 vCPUs, 7.5 GiB memory, EBS Only)'),
    ('c4.2xlarge', 'c4.2xlarge (8 vCPUs, 15 GiB memory, EBS Only)'),
    ('c4.4xlarge', 'c4.4xlarge (16 vCPUs, 30 GiB memory, EBS Only)'),
    ('c4.8xlarge', 'c4.8xlarge (36 vCPUs, 60 GiB memory, EBS Only)'),
    ('c3.large', 'c3.large (2 vCPUs, 3.75 GiB memory, 2 x 16 GiB SSD Storage Capacity)'),
    ('c3.xlarge', 'c3.xlarge (4 vCPUs, 7.5 GiB memory, 2 x 40 GiB SSD Storage Capacity)'),
    ('c3.2xlarge', 'c3.2xlarge (8 vCPUs, 15 GiB memory, 2 x 80 GiB SSD Storage Capacity)'),
    ('c3.4xlarge', 'c3.4xlarge (16 vCPUs, 30 GiB memory, 2 x 160 GiB SSD Storage Capacity)'),
    ('c3.8xlarge', 'c3.8xlarge (32 vCPUs, 60 GiB memory, 2 x 320 GiB SSD Storage Capacity)'),
    ('g2.2xlarge', 'g2.2xlarge (8 vCPUs, 15 GiB memory, 1 x 60 GiB SSD Storage Capacity)'),
    ('g2.4xlarge', 'g2.4xlarge (32 vCPUs, 60 GiB memory, 2 x 120 GiB SSD Storage Capacity)'),
    ('r3.large', 'r3.large (2 vCPUs, 15.25 GiB memory, 1 x 32 GiB SSD Storage Capacity)'),
    ('r3.xlarge', 'r3.xlarge (4 vCPUs, 30.5 GiB memory, 1 x 80 GiB SSD Storage Capacity)'),
    ('r3.2xlarge', 'r3.2xlarge (8 vCPUs, 61 GiB memory, 1 x 160 GiB SSD Storage Capacity)'),
    ('r3.4xlarge', 'r3.4xlarge (16 vCPUs, 122 GiB memory, 1 x 320 GiB SSD Storage Capacity)'),
    ('r3.8xlarge', 'r3.8xlarge (32 vCPUs, 244 GiB memory, 2 x 320 GiB SSD Storage Capacity)'),
    ('i2.xlarge', 'i2.xlarge (4 vCPUs, 30.5 GiB memory, 1 x 800 GiB SSD Storage Capacity)'),
    ('i2.2xlarge', 'i2.2xlarge (8 vCPUs, 61 GiB memory, 2 x 800 GiB SSD Storage Capacity)'),
    ('i2.4xlarge', 'i2.4xlarge (16 vCPUs, 122 GiB memory, 4 x 800 GiB SSD Storage Capacity)'),
    ('i2.8xlarge', 'i2.8xlarge (32 vCPUs, 244 GiB memory, 8 x 800 GiB SSD Storage Capacity)'),
    ('d2.xlarge', 'd2.xlarge (4 vCPUs, 30.5 GiB memory, 3 x 2000 GiB Storage Capacity)'),
    ('d2.2xlarge', 'd2.2xlarge (8 vCPUs, 61 GiB memory, 6 x 2000 GiB Storage Capacity)'),
    ('d2.4xlarge', 'd2.4xlarge (16 vCPUs, 122 GiB memory, 12 x 2000 GiB Storage Capacity)'),
    ('d2.8xlarge', 'd2.8xlarge (36 vCPUs, 244 GiB memory, 24 x 2000 GiB Storage Capacity)'),
]


INSTANCE_MONITORING_CHARTS_LIST = [
    {
        'metric': 'CPUUtilization',
        'unit': 'Percent',
    },
    {
        'metric': 'DiskReadBytes',
        'unit': 'Bytes',
    },
    {
        'metric': 'DiskReadOps',
        'unit': 'Count',
    },
    {
        'metric': 'DiskWriteBytes',
        'unit': 'Bytes',
    },
    {
        'metric': 'DiskWriteOps',
        'unit': 'Count',
    },
    {
        'metric': 'NetworkIn',
        'unit': 'Bytes',
    },
    {
        'metric': 'NetworkOut',
        'unit': 'Bytes',
    },
]
