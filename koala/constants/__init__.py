# -*- coding: utf-8 -*-
"""
Common constants

"""


# AWS Regions
# Note: We could pull these from boto.ec2.regions(), but they don't change too often so let's hard-code them here.
# Use a data structure to support multiple endpoint types, with EC2 per se for now.
AWS_REGIONS = (
    dict(
        name='us-east-1',
        label='US East (N. Virginia)',
        endpoints=dict(ec2='ec2.us-east-1.amazonaws.com'),
    ),
    dict(
        name='us-west-1',
        label='US West (N. California)',
        endpoints=dict(ec2='ec2.us-west-1.amazonaws.com'),
    ),
    dict(
        name='us-west-2',
        label='US West (Oregon)',
        endpoints=dict(ec2='ec2.us-west-2.amazonaws.com')
    ),
    dict(
        name='eu-west-1',
        label='EU (Ireland)',
        endpoints=dict(ec2='ec2.eu-west-1.amazonaws.com')
    ),
    dict(
        name='ap-southeast-1',
        label='Asia Pacific (Singapore)',
        endpoints=dict(ec2='ec2.ap-southeast-1.amazonaws.com')
    ),
    dict(
        name='ap-southeast-2',
        label='Asia Pacific (Sydney)',
        endpoints=dict(ec2='ec2.ap-southeast-2.amazonaws.com')
    ),
    dict(
        name='ap-northeast-1',
        label='Asia Pacific (Tokyo)',
        endpoints=dict(ec2='ec2.ap-northeast-1.amazonaws.com')
    ),
    dict(
        name='sa-east-1',
        label=u'South America (São Paulo)',
        endpoints=dict(ec2='ec2.sa-east-1.amazonaws.com')
    ),
)

