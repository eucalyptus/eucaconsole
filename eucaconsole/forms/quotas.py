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
Form for Quotas 

"""
import simplejson as json

from boto.exception import BotoServerError

import wtforms

from ..i18n import _
from . import BaseSecureForm


class QuotasForm(BaseSecureForm):
    """User form
       Note: no need to add a 'users' field.  Use the user_editor panel (in a template) instead
       Only need to initialize as a secure form to generate CSRF token
    """
    ec2_images_max = wtforms.TextField(label=_(u'Images (maximum)'))
    ec2_instances_max = wtforms.TextField(label=_(u'Instances (maximum)'))
    ec2_volumes_max = wtforms.TextField(label=_(u'Volumes (maximum)'))
    ec2_total_size_all_vols = wtforms.TextField(label=_(u'Total size of all volumes (GB)'))
    ec2_snapshots_max = wtforms.TextField(label=_(u'Snapshots (maximum)'))
    ec2_elastic_ip_max = wtforms.TextField(label=_(u'Elastic IP addresses (maximum)'))

    s3_buckets_max = wtforms.TextField(label=_(u'Buckets (maximum)'))
    s3_objects_per_max = wtforms.TextField(label=_(u'Objects per bucket (maximum)'))
    s3_bucket_size = wtforms.TextField(label=_(u'Size of each bucket (MB)'))
    s3_total_size_all_buckets = wtforms.TextField(label=_(u'Total size of all buckets (maximum)'))

    autoscale_groups_max = wtforms.TextField(label=_(u'Auto scaling groups (maximum)'))
    launch_configs_max = wtforms.TextField(label=_(u'Launch configurations (maximum)'))
    scaling_policies_max = wtforms.TextField(label=_(u'Scaling policies (maximum)'))

    elb_load_balancers_max = wtforms.TextField(label=_(u'Load balancers (maximum)'))

    iam_groups_max = wtforms.TextField(label=_(u'Groups (maximum)'))
    iam_users_max = wtforms.TextField(label=_(u'Users (maximum)'))
    iam_roles_max = wtforms.TextField(label=_(u'Roles (maximum)'))
    iam_inst_profiles_max = wtforms.TextField(label=_(u'Instance profiles (maximum)'))

    def __init__(self, request, user=None, account=None, conn=None, **kwargs):
        super(QuotasForm, self).__init__(request, **kwargs)
        if user is not None:
            try:
                policies = conn.get_all_user_policies(user_name=user.user_name)
                for policy_name in policies.policy_names:
                    policy_json = conn.get_user_policy(user_name=user.user_name,
                                        policy_name=policy_name).policy_document
                    self.scan_policy(policy_json)
            except BotoServerError as err:
                pass
        if account is not None:
            try:
                policies = conn.get_response(
                            'ListAccountPolicies',
                            params={'AccountName':account.account_name}, list_marker='PolicyNames')
                
                for policy_name in policies.policy_names:
                    policy_json = conn.get_response(
                            'GetAccountPolicy',
                            params={'AccountName':account.account_name, 'PolicyName':policy_name}, verb='POST').policy_document
                    self.scan_policy(policy_json)
            except BotoServerError as err:
                pass

    def scan_policy(self, policy_json):
        policy = json.loads(policy_json)
        for s in policy['Statement']:
            try:    # skip statements without conditions
                s['Condition']
            except KeyError:
                continue
            for cond in s['Condition'].keys():
                if cond == "NumericLessThanEquals": 
                    for val in s['Condition'][cond].keys():
                        limit = s['Condition'][cond][val]
                        if val == 'ec2:quota-imagenumber':
                            self.set_lowest(self.ec2_images_max, limit)
                        elif val == 'ec2:quota-vminstancenumber':
                            self.set_lowest(self.ec2_instances_max, limit)
                        elif val == 'ec2:quota-volumenumber':
                            self.set_lowest(self.ec2_volumes_max, limit)
                        elif val == 'ec2:quota-snapshotnumber':
                            self.set_lowest(self.ec2_snapshots_max, limit)
                        elif val == 'ec2:quota-volumetotalsize':
                            self.set_lowest(self.ec2_total_size_all_vols, limit)
                        elif val == 'ec2:quota-addressnumber':
                            self.set_lowest(self.ec2_elastic_ip_max, limit)
                        elif val == 's3:quota-bucketnumber':
                            self.set_lowest(self.s3_buckets_max, limit)
                        elif val == 's3:quota-bucketobjectnumber':
                            self.set_lowest(self.s3_objects_per_max, limit)
                        elif val == 's3:quota-bucketsize':
                            self.set_lowest(self.s3_bucket_size, limit)
                        elif val == 's3:quota-buckettotalsize':
                            self.set_lowest(self.s3_total_size_all_buckets, limit)
                        elif val == 'autoscaling:quota-autoscalinggroupnumber':
                            self.set_lowest(self.autoscale_groups_max, limit)
                        elif val == 'autoscaling:quota-launchconfigurationnumber':
                            self.set_lowest(self.launch_configs_max, limit)
                        elif val == 'autoscaling:quota-scalingpolicynumber':
                            self.set_lowest(self.scaling_policies_max, limit)
                        elif val == 'elasticloadbalancing:quota-loadbalancernumber':
                            self.set_lowest(self.elb_load_balancers_max, limit)
                        elif val == 'iam:quota-groupnumber':
                            self.set_lowest(self.iam_groups_max, limit)
                        elif val == 'iam:quota-usernumber':
                            self.set_lowest(self.iam_users_max, limit)
                        elif val == 'iam:quota-rolenumber':
                            self.set_lowest(self.iam_roles_max, limit)
                        elif val == 'iam:quota-instanceprofilenumber':
                            self.set_lowest(self.iam_inst_profiles_max, limit)

    def set_lowest(self, item, val):
        """ This function sets the field data value if the new value is lower than the current one """
        if item.data is None or item.data > val:
            item.data = val

