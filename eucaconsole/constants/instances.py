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
    ('t1.micro', 't1.micro (up to 2 ECUs, 1 vCPUs, 0.613 GiB memory, EBS only)'),
    ('m1.small', 'm1.small (1 ECUs, 1 vCPUs, 1.7 GiB memory, 1 x 160 GiB Storage Capacity)'),
    ('m1.medium', 'm1.medium (2 ECUs, 1 vCPUs, 3.7 GiB memory, 1 x 410 GiB Storage Capacity)'),
    ('m1.large', 'm1.large (4 ECUs, 2 vCPUs, 7.5 GiB memory, 2 x 420 GiB Storage Capacity)'),
    ('m1.xlarge', 'm1.xlarge (8 ECUs, 4 vCPUs, 15 GiB memory, 4 x 420 GiB Storage Capacity)'),
    ('m2.xlarge', 'm2.xlarge (6.5 ECUs, 2 vCPUs, 17.1 GiB memory, 1 x 420 GiB Storage Capacity)'),
    ('m2.2xlarge', 'm2.2xlarge (13 ECUs, 4 vCPUs, 34.2 GiB memory, 1 x 850 GiB Storage Capacity)'),
    ('m2.4xlarge', 'm2.4xlarge (26 ECUs, 8 vCPUs, 68.4 GiB memory, 2 x 840 GiB Storage Capacity)'),
    ('cr1.8xlarge', ' cr1.8xlarge (88 ECUs, 32 vCPUs, 244 GiB memory, 2 x 120 GiB SSD Storage Capacity)'),
    ('m3.medium', ' m3.medium (3 ECUs, 1 vCPUs, 3.75 GiB memory, 1 x 4 GiB SSD Storage Capacity)'),
    ('m3.large', ' m3.large (6.5 ECUs, 2 vCPUs, 7.5 GiB memory, 1 x 32 GiB SSD Storage Capacity)'),
    ('m3.xlarge', ' m3.xlarge (13 ECUs, 4 vCPUs, 15 GiB memory, 2 x 40 GiB SSD Storage Capacity)'),
    ('m3.2xlarge', 'm3.2xlarge (26 ECUs, 8 vCPUs, 30 GiB memory, 2 x 80 GiB SSD Storage Capacity)'),
    ('c1.medium', 'c1.medium (5 ECUs, 2 vCPUs, 1.7 GiB memory, 1 x 350 GiB Storage Capacity)'),
    ('c1.xlarge', 'c1.xlarge (20 ECUs, 8 vCPUs, 7 GiB memory, 4 x 420 GiB Storage Capacity)'),
    ('cc2.8xlarge', 'cc2.8xlarge (88 ECUs, 32 vCPUs, 60.5 GiB memory, 4 x 840 GiB Storage Capacity)'),
    ('c3.large', 'c3.large (7 ECUs, 2 vCPUs, 3.75 GiB memory, 2 x 16 GiB Storage Capacity)'),
    ('c3.xlarge', 'c3.xlarge (14 ECUs, 4 vCPUs, 7.5 GiB memory, 2 x 40 GiB Storage Capacity)'),
    ('c3.2xlarge', 'c3.2xlarge (28 ECUs, 8 vCPUs, 15 GiB memory, 2 x 80 GiB Storage Capacity)'),
    ('c3.4xlarge', 'c3.4xlarge (55 ECUs, 16 vCPUs, 30 GiB memory, 2 x 160 GiB Storage Capacity)'),
    ('c3.8xlarge', 'c3.8xlarge (108 ECUs, 32 vCPUs, 60 GiB memory, 2 x 320 GiB Storage Capacity)'),
    ('g2.2xlarge', 'g2.2xlarge (26 ECUs, 8 vCPUs, 15 GiB memory, 1 x 60 GiB SSD Storage Capacity)'),
    ('cg1.4xlarge', 'cg1.4xlarge (33.5 ECUs, 16 vCPUs, 22.5 GiB memory, 2 x 840 GiB Storage Capacity)'),
    ('r3.large', 'r3.large (2 vCPUs, 15 GiB memory, 1 x 32 GiB SSD Storage Capacity)'),
    ('r3.xlarge', 'r3.xlarge (4 vCPUs, 30.5 GiB memory, 1 x 80 GiB SSD Storage Capacity)'),
    ('r3.2xlarge', 'r3.2xlarge (8 vCPUs, 61 GiB memory, 1 x 160 GiB SSD Storage Capacity)'),
    ('r3.4xlarge', 'r3.4xlarge (16 vCPUs, 122 GiB memory, 1 x 320 GiB SSD Storage Capacity)'),
    ('r3.8xlarge', 'r3.8xlarge (32 vCPUs, 244 GiB memory, 2 x 320 GiB SSD Storage Capacity)'),
    ('i2.xlarge', 'i2.xlarge (14 ECUs, 4 vCPUs, 30.5 GiB memory, 1 x 800 GiB SSD Storage Capacity)'),
    ('i2.2xlarge', 'i2.2xlarge (27 ECUs, 8 vCPUs, 61 GiB memory, 2 x 800 GiB SSD Storage Capacity)'),
    ('i2.4xlarge', 'i2.4xlarge (53 ECUs, 16 vCPUs, 122 GiB memory, 4 x 800 GiB SSD Storage Capacity)'),
    ('i2.8xlarge', 'i2.8xlarge (104 ECUs, 32 vCPUs, 244 GiB memory, 8 x 800 GiB SSD Storage Capacity)'),
    ('hi1.4xlarge', 'hi1.4xlarge (35 ECUs, 16 vCPUs, 60.5 GiB memory, 2 x 1024 GiB SSD Storage Capacity)'),
    ('hs1.8xlarge', 'hs1.8xlarge (35 ECUs, 16 vCPUs, 117 GiB memory, 24 x 2048 GiB Storage Capacity)'),
]


