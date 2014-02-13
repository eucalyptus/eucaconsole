# -*- coding: utf-8 -*-
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


