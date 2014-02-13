# -*- coding: utf-8 -*-
"""
Access policies

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


# Listing of Possible Policy Generator Actions
POLICY_ACTIONS = {
    'EC2': [
        'ActivateLicense',
        'AllocateAddress',
        'AssignPrivateIpAddresses',
        'AssociateAddress',
        'AssociateDhcpOptions',
        'AssociateRouteTable',
        'AttachInternetGateway',
        'AttachNetworkInterface',
        'AttachVolume',
        'AttachVpnGateway',
        'AuthorizeSecurityGroupEgress',
        'AuthorizeSecurityGroupIngress',
        'BundleInstance',
        'CancelBundleTask',
        'CancelConversionTask',
        'CancelExportTask',
        'CancelReservedInstancesListing',
        'CancelSpotInstanceRequests',
        'ConfirmProductInstance',
        'CopyImage',
        'CopySnapshot',
        'CreateCustomerGateway',
        'CreateDhcpOptions',
        'CreateImage',
        'CreateInstanceExportTask',
        'CreateInternetGateway',
        'CreateKeyPair',
        'CreateNetworkAcl',
        'CreateNetworkAclEntry',
        'CreateNetworkInterface',
        'CreatePlacementGroup',
        'CreateReservedInstancesListing',
        'CreateRoute',
        'CreateRouteTable',
        'CreateSecurityGroup',
        'CreateSnapshot',
        'CreateSpotDatafeedSubscription',
        'CreateSubnet',
        'CreateTags',
        'CreateVolume',
        'CreateVpc',
        'CreateVpnConnection',
        'CreateVpnConnectionRoute',
        'CreateVpnGateway',
        'DeactivateLicense',
        'DeleteCustomerGateway',
        'DeleteDhcpOptions',
        'DeleteInternetGateway',
        'DeleteKeyPair',
        'DeleteNetworkAcl',
        'DeleteNetworkAclEntry',
        'DeleteNetworkInterface',
        'DeletePlacementGroup',
        'DeleteRoute',
        'DeleteRouteTable',
        'DeleteSecurityGroup',
        'DeleteSnapshot',
        'DeleteSpotDatafeedSubscription',
        'DeleteSubnet',
        'DeleteTags',
        'DeleteVolume',
        'DeleteVpc',
        'DeleteVpnConnection',
        'DeleteVpnConnectionRoute',
        'DeleteVpnGateway',
        'DeregisterImage',
        'DescribeAccountAttributes',
        'DescribeAddresses',
        'DescribeAvailabilityZones',
        'DescribeBundleTasks',
        'DescribeConversionTasks',
        'DescribeCustomerGateways',
        'DescribeDhcpOptions',
        'DescribeExportTasks',
        'DescribeImageAttribute',
        'DescribeImages',
        'DescribeInstanceAttribute',
        'DescribeInstanceStatus',
        'DescribeInstances',
        'DescribeInternetGateways',
        'DescribeKeyPairs',
        'DescribeLicenses',
        'DescribeNetworkAcls',
        'DescribeNetworkInterfaceAttribute',
        'DescribeNetworkInterfaces',
        'DescribePlacementGroups',
        'DescribeRegions',
        'DescribeReservedInstances',
        'DescribeReservedInstancesListings',
        'DescribeReservedInstancesModifications',
        'DescribeReservedInstancesOfferings',
        'DescribeRouteTables',
        'DescribeSecurityGroups',
        'DescribeSnapshotAttribute',
        'DescribeSnapshots',
        'DescribeSpotDatafeedSubscription',
        'DescribeSpotInstanceRequests',
        'DescribeSpotPriceHistory',
        'DescribeSubnets',
        'DescribeTags',
        'DescribeVolumeAttribute',
        'DescribeVolumeStatus',
        'DescribeVolumes',
        'DescribeVpcAttribute',
        'DescribeVpcs',
        'DescribeVpnConnections',
        'DescribeVpnGateways',
        'DetachInternetGateway',
        'DetachNetworkInterface',
        'DetachVolume',
        'DetachVpnGateway',
        'DisableVgwRoutePropagation',
        'DisassociateAddress',
        'DisassociateRouteTable',
        'EnableVgwRoutePropagation',
        'EnableVolumeIO',
        'GetConsoleOutput',
        'GetPasswordData',
        'ImportInstance',
        'ImportKeyPair',
        'ImportVolume',
        'ModifyImageAttribute',
        'ModifyInstanceAttribute',
        'ModifyNetworkInterfaceAttribute',
        'ModifyReservedInstances',
        'ModifySnapshotAttribute',
        'ModifyVolumeAttribute',
        'ModifyVpcAttribute',
        'MonitorInstances',
        'PurchaseReservedInstancesOffering',
        'RebootInstances',
        'RegisterImage',
        'ReleaseAddress',
        'ReplaceNetworkAclAssociation',
        'ReplaceNetworkAclEntry',
        'ReplaceRoute',
        'ReplaceRouteTableAssociation',
        'ReportInstanceStatus',
        'RequestSpotInstances',
        'ResetImageAttribute',
        'ResetInstanceAttribute',
        'ResetNetworkInterfaceAttribute',
        'ResetSnapshotAttribute',
        'RevokeSecurityGroupEgress',
        'RevokeSecurityGroupIngress',
        'RunInstances',
        'StartInstances',
        'StopInstances',
        'TerminateInstances',
        'UnassignPrivateIpAddresses',
        'UnmonitorInstances',
    ]
}


