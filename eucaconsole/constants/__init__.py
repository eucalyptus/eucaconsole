# -*- coding: utf-8 -*-
# Copyright 2013-2017 Ent. Services Development Corporation LP
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


# AWS Regions list
# Endpoints are handled via boto's endpoints.json
# Note: A future release of the Eucalyptus console will pull regions via the DescribeRegions API call
AWS_REGIONS = [
    dict(
        name='us-east-1',
        label='US East (N. Virginia)',
    ),
    dict(
        name='us-east-2',
        label='US East (Ohio)',
    ),
    dict(
        name='us-west-1',
        label='US West (N. California)',
    ),
    dict(
        name='us-west-2',
        label='US West (Oregon)',
    ),
    dict(
        name='ca-central-1',
        label='Canada (Central)',
    ),
    dict(
        name='eu-west-1',
        label='EU (Ireland)',
    ),
    dict(
        name='eu-west-2',
        label='EU (London)',
    ),
    dict(
        name='eu-central-1',
        label='EU (Frankfurt)',
    ),
    dict(
        name='ap-south-1',
        label='Asia Pacific (Mumbai)',
    ),
    dict(
        name='ap-southeast-1',
        label='Asia Pacific (Singapore)',
    ),
    dict(
        name='ap-southeast-2',
        label='Asia Pacific (Sydney)',
    ),
    dict(
        name='ap-northeast-1',
        label='Asia Pacific (Tokyo)',
    ),
    dict(
        name='ap-northeast-2',
        label='Asia Pacific (Seoul)',
    ),
    dict(
        name='sa-east-1',
        label=u'South America (São Paulo)',
    ),
]


# List of all landing page route names (used to limit redirect handling for AWS region selection)
LANDINGPAGE_ROUTE_NAMES = [
    'buckets', 'groups', 'images', 'instances', 'ipaddresses', 'keypairs', 'launchconfigs',
    'scalinggroups', 'securitygroups', 'snapshots', 'users', 'volumes', 'elbs', 'stacks',
    'cloudwatch_alarms', 'cloudwatch_metrics'
]

