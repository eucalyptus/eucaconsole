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


# List of all landing page route names (used to limit redirect handling for AWS region selection)
LANDINGPAGE_ROUTE_NAMES = [
    'buckets', 'groups', 'images', 'instances', 'ipaddresses', 'keypairs', 'launchconfigs',
    'scalinggroups', 'securitygroups', 'snapshots', 'users', 'volumes',
]

