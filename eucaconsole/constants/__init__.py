# _*_ coding: utf_8 _*_
# Copyright 2013_2017 Ent. Services Development Corporation LP
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
AWS_REGIONS = {
    'us-east-1': 'US East (N. Virginia)',
    'us-east-2': 'US East (Ohio)',
    'us-west-1': 'US West (N. California)',
    'us-west-2': 'US West (Oregon)',
    'ca-central-1': 'Canada (Central)',
    'eu-west-1': 'EU (Ireland)',
    'eu-west-2': 'EU (London)',
    'eu-central-1': 'EU (Frankfurt)',
    'ap-south-1': 'Asia Pacific (Mumbai)',
    'ap-southeast-1': 'Asia Pacific (Singapore)',
    'ap-southeast-2': 'Asia Pacific (Sydney)',
    'ap-northeast-1': 'Asia Pacific (Tokyo)',
    'ap-northeast-2': 'Asia Pacific (Seoul)',
    'sa-east-1': u'South America (São Paulo)',
}


# List of all landing page route names (used to limit redirect handling for AWS region selection)
LANDINGPAGE_ROUTE_NAMES = [
    'buckets', 'groups', 'images', 'instances', 'ipaddresses', 'keypairs', 'launchconfigs',
    'scalinggroups', 'securitygroups', 'snapshots', 'users', 'volumes', 'elbs', 'stacks',
    'cloudwatch_alarms', 'cloudwatch_metrics', 'queues', 'vpcs'
]

