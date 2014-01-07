# -*- coding: utf-8 -*-
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
    ('m3.xlarge', ' m3.xlarge (13 ECUs, 4 vCPUs, 15 GiB memory, 2 x 40 GiB Storage Capacity)'),
    ('m3.2xlarge', 'm3.2xlarge (26 ECUs, 8 vCPUs, 30 GiB memory, 2 x 80 GiB Storage Capacity)'),
    ('m2.xlarge', 'm2.xlarge (6.5 ECUs, 2 vCPUs, 17.1 GiB memory, 1 x 420 GiB Storage Capacity)'),
    ('m2.2xlarge', 'm2.2xlarge (13 ECUs, 4 vCPUs, 34.2 GiB memory, 1 x 850 GiB Storage Capacity)'),
    ('m2.4xlarge', 'm2.4xlarge (26 ECUs, 8 vCPUs, 68.4 GiB memory, 2 x 840 GiB Storage Capacity)'),
    ('hi1.4xlarge', 'hi1.4xlarge (35 ECUs, 16 vCPUs, 60.5 GiB memory, 2 x 1024 GiB Storage Capacity)'),
    ('hs1.8xlarge', 'hs1.8xlarge (35 ECUs, 16 vCPUs, 117 GiB memory, 24 x 2048 GiB Storage Capacity)'),
    ('c1.medium', 'c1.medium (5 ECUs, 2 vCPUs, 1.7 GiB memory, 1 x 350 GiB Storage Capacity)'),
    ('c1.xlarge', 'c1.xlarge (20 ECUs, 8 vCPUs, 7 GiB memory, 4 x 420 GiB Storage Capacity)'),
    ('c3.large', 'c3.large (7 ECUs, 2 vCPUs, 3.75 GiB memory, 2 x 16 GiB Storage Capacity)'),
    ('c3.xlarge', 'c3.xlarge (14 ECUs, 4 vCPUs, 7.5 GiB memory, 2 x 40 GiB Storage Capacity)'),
    ('c3.2xlarge', 'c3.2xlarge (28 ECUs, 8 vCPUs, 15 GiB memory, 2 x 80 GiB Storage Capacity)'),
    ('c3.4xlarge', 'c3.4xlarge (55 ECUs, 16 vCPUs, 30 GiB memory, 2 x 160 GiB Storage Capacity)'),
    ('c3.8xlarge', 'c3.8xlarge (108 ECUs, 32 vCPUs, 60 GiB memory, 2 x 320 GiB Storage Capacity)'),
]


