# -*- coding: utf-8 -*-
"""
Eucalyptus and AWS Instance constants

"""


# TODO: Use DescribeInstanceTypes instead of these values
EUCA_INSTANCE_TYPE_CHOICES = [
    ('t1.micro', 't1.micro: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)'),
    ('m1.small', 'm1.small: 1 CPUs, 256 memory (MB), 5 disk (GB,root device)'),
    ('m1.medium', 'm1.medium: 1 CPUs, 512 memory (MB), 10 disk (GB,root device)'),
    ('m1.large', 'm1.large: 2 CPUs, 512 memory (MB), 10 disk (GB,root device)'),
    ('m1.xlarge', 'm1.xlarge: 2 CPUs, 1024 memory (MB), 10 disk (GB,root device)'),
    ('m2.xlarge', 'm2.xlarge: 2 CPUs, 2048 memory (MB), 10 disk (GB,root device)'),
    ('m2.2xlarge', 'm2.2xlarge: 2 CPUs, 4096 memory (MB), 30 disk (GB,root device)'),
    ('m2.4xlarge', 'm2.4xlarge: 8 CPUs, 4096 memory (MB), 60 disk (GB,root device)'),
    ('m3.xlarge', 'm3.xlarge: 4 CPUs, 2048 memory (MB), 15 disk (GB,root device)'),
    ('m3.2xlarge', 'm3.2xlarge: 4 CPUs, 4096 memory (MB), 30 disk (GB,root device)'),
    ('c1.medium', 'c1.medium: 2 CPUs, 512 memory (MB), 10 disk (GB,root device)'),
    ('c1.xlarge', 'c1.xlarge: 2 CPUs, 2048 memory (MB), 10 disk (GB,root device)'),
    ('cc1.4xlarge', 'cc1.4xlarge: 8 CPUs, 3072 memory (MB), 60 disk (GB,root device)'),
    ('cc2.8xlarge', 'cc2.8xlarge: 16 CPUs, 6144 memory (MB), 120 disk (GB,root device)'),
    ('cr1.8xlarge', 'cr1.8xlarge: 16 CPUs, 16384 memory (MB), 240 disk (GB,root device)'),
    ('cg1.4xlarge', 'cg1.4xlarge: 16 CPUs, 12288 memory (MB), 200 disk (GB,root device)'),
    ('hi1.4xlarge', 'hi1.4xlarge: 8 CPUs, 6144 memory (MB), 120 disk (GB,root device)'),
    ('hs1.8xlarge', 'hs1.8xlarge: 48 CPUs, 119808 memory (MB), 24000 disk (GB,root device)'),
]

# TODO: Confirm we have the most recent list of choices here
AWS_INSTANCE_TYPE_CHOICES = EUCA_INSTANCE_TYPE_CHOICES


