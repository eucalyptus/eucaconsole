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
Constants for Access policies

"""

API_VERSION = "2012-10-17"

# Admin access policy (full access, including users/groups)
ADMIN_ACCESS_POLICY = {
    "Version": API_VERSION,
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        }
    ]
}


# Power user access policy (full access, except users/groups)
USER_ACCESS_POLICY = {
    "Version": API_VERSION,
    "Statement": [
        {
            "Effect": "Allow",
            "NotAction": "iam:*",
            "Resource": "*"
        }
    ]
}


# Monitor/readonly access policy (except users/groups)
MONITOR_ACCESS_POLICY = {
    "Version": API_VERSION,
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:Describe*",
                "cloudwatch:Describe*",
                "cloudwatch:Get*",
                "cloudwatch:List*",
                "ec2:Describe*",
                "s3:Get*",
                "s3:List*",
            ],
            "Resource": "*"
        }
    ]
}


# Starter template for empty access policy (advanced option in wizard)
BLANK_POLICY = {
    "Version": API_VERSION,
    "Statement": [
        {
            "Effect": "",
            "Action": [],
            "Resource": ""
        }
    ]
}

TYPE_POLICY_MAPPING = {
    'admin_access': ADMIN_ACCESS_POLICY,
    'user_access': USER_ACCESS_POLICY,
    'monitor_access': MONITOR_ACCESS_POLICY,
    'blank': BLANK_POLICY,
}


