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

from ..i18n import _
import simplejson as json
import sys

"""
Quota handling code

"""
class Quotas(object):
    EUCA_DEFAULT_POLICY = 'euca-console-quota-policy'

    def add_quota_limit(self, view, statements, param, action, condition):
        val = view.request.params.get(param, None)
        if val:
            statements.append({
                'Effect': 'Limit', 'Action': action, 'Resource': '*',
                'Condition': {'NumericLessThanEquals': {condition: val}}
            })

    def create_quota_policy(self, view, user=None, account=None, as_account=''):
        policy = {'Version': '2011-04-01'}
        statements = []
        # now, look at quotas
        ## ec2
        self.add_quota_limit(
            view, statements, 'ec2_images_max', 'ec2:RegisterImage', 'ec2:quota-imagenumber')
        self.add_quota_limit(
            view, statements, 'ec2_instances_max', 'ec2:RunInstances', 'ec2:quota-vminstancenumber')
        self.add_quota_limit(
            view, statements, 'ec2_volumes_max', 'ec2:CreateVolume', 'ec2:quota-volumenumber')
        self.add_quota_limit(
            view, statements, 'ec2_snapshots_max', 'ec2:CreateSnapshot', 'ec2:quota-snapshotnumber')
        self.add_quota_limit(
            view, statements, 'ec2_elastic_ip_max', 'ec2:AllocateAddress', 'ec2:quota-addressnumber')
        self.add_quota_limit(
            view, statements, 'ec2_total_size_all_vols', 'ec2:Createvolume', 'ec2:quota-volumetotalsize')
        ## s3
        self.add_quota_limit(
            view, statements, 's3_buckets_max', 's3:CreateBucket', 's3:quota-bucketnumber')
        self.add_quota_limit(
            view, statements, 's3_objects_per_max', 's3:CreateObject', 's3:quota-bucketobjectnumber')
        self.add_quota_limit(
            view, statements, 's3_bucket_size', 's3:PutObject', 's3:quota-bucketsize')
        self.add_quota_limit(
            view, statements, 's3_total_size_all_buckets', 's3:pubobject', 's3:quota-buckettotalsize')
        ## iam
        self.add_quota_limit(
            view, statements, 'iam_groups_max', 'iam:CreateGroup', 'iam:quota-groupnumber')
        self.add_quota_limit(
            view, statements, 'iam_users_max', 'iam:CreateUser', 'iam:quota-usernumber')
        self.add_quota_limit(
            view, statements, 'iam_roles_max', 'iam:CreateRole', 'iam:quota-rolenumber')
        self.add_quota_limit(
            view, statements, 'iam_inst_profiles_max',
            'iam:CreateInstanceProfile', 'iam:quota-instanceprofilenumber')
        ## autoscaling
        self.add_quota_limit(
            view, statements, 'autoscale_groups_max', 'autoscaling:createautoscalinggroup',
            'autoscaling:quota-autoscalinggroupnumber')
        self.add_quota_limit(
            view, statements, 'launch_configs_max', 'autoscaling:createlaunchconfiguration',
            'autoscaling:quota-launchconfigurationnumber')
        self.add_quota_limit(
            view, statements, 'scaling_policies_max', 'autoscaling:pubscalingpolicy',
            'autoscaling:quota-scalingpolicynumber')
        ## elb
        self.add_quota_limit(
            view, statements, 'elb_load_balancers_max', 'elasticloadbalancing:createloadbalancer',
            'elasticloadbalancing:quota-loadbalancernumber')

        if len(statements) > 0:
            policy['Statement'] = statements
            if user is not None:
                view.log_request(_(u"Creating policy for user {0}").format(user))
                view.conn.get_response('PutUserPolicy', params={'UserName':user, 'PolicyName':self.EUCA_DEFAULT_POLICY, 'PolicyDocument':json.dumps(policy), 'DelegateAccount':as_account})
            if account is not None:
                view.log_request(_(u"Creating policy for account {0}").format(account))
                view.conn.get_response('PutAccountPolicy', params={'AccountName':account, 'PolicyName':self.EUCA_DEFAULT_POLICY, 'PolicyDocument':json.dumps(policy), 'DelegateAccount':as_account})

    def update_quotas(self, view, user=None, account=None, as_account=''):
            # load all policies for this user
            policy_list = []
            if user is not None:
                policies = view.conn.get_response(
                        'ListUserPolicies',
                        params={'UserName':user, 'DelegateAccount':as_account}, list_marker='PolicyNames')
            if account is not None:
                policies = view.conn.get_response(
                        'ListAccountPolicies',
                        params={'AccountName':account, 'DelegateAccount':as_account}, list_marker='PolicyNames')
            for policy_name in policies.policy_names:
                if user is not None:
                    policy_json = view.conn.get_response(
                        'GetUserPolicy',
                        params={'UserName':user, 'PolicyName':policy_name, 'DelegateAccount':as_account}, verb='POST').policy_document
                    policy = json.loads(policy_json)
                    policy_list.append(policy)
                if account is not None:
                    policy_json = view.conn.get_response(
                        'GetAccountPolicy',
                        params={'AccountName':account, 'PolicyName':policy_name, 'DelegateAccount':as_account}, verb='POST').policy_document
                    policy = json.loads(policy_json)
                    policy_list.append(policy)
            # for each form item, update proper policy if needed
            new_stmts = []
            ## ec2
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'ec2_images_max', 'ec2:RegisterImage', 'ec2:quota-imagenumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'ec2_instances_max', 'ec2:RunInstances', 'ec2:quota-vminstancenumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'ec2_volumes_max', 'ec2:CreateVolume', 'ec2:quota-volumenumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'ec2_snapshots_max', 'ec2:CreateSnapshot', 'ec2:quota-snapshotnumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'ec2_elastic_ip_max', 'ec2:AllocateAddress', 'ec2:quota-addressnumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'ec2_total_size_all_vols', 'ec2:Createvolume', 'ec2:quota-volumetotalsize')
            ## s3
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    's3_buckets_max', 's3:CreateBucket', 's3:quota-bucketnumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    's3_objects_per_max', 's3:CreateObject', 's3:quota-bucketobjectnumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    's3_bucket_size', 's3:PutObject', 's3:quota-bucketsize')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    's3_total_size_all_buckets', 's3:pubobject', 's3:quota-buckettotalsize')
            ## iam
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'iam_groups_max', 'iam:CreateGroup', 'iam:quota-groupnumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'iam_users_max', 'iam:CreateUser', 'iam:quota-usernumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'iam_roles_max', 'iam:CreateRole', 'iam:quota-rolenumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'iam_inst_profiles_max', 'iam:CreateInstanceProfile',
                                    'iam:quota-instanceprofilenumber')
            ## autoscaling
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'autoscale_groups_max', 'autoscaling:createautoscalinggroup',
                                    'autoscaling:quota-autoscalinggroupnumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'launch_configs_max', 'autoscaling:createlaunchconfiguration',
                                    'autoscaling:quota-launchconfigurationnumber')
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'scaling_policies_max', 'autoscaling:pubscalingpolicy',
                                    'autoscaling:quota-scalingpolicynumber')
            ## elb
            self._update_quota_limit_(view, policy_list, new_stmts,
                                    'elb_load_balancers_max', 'elasticloadbalancing:createloadbalancer',
                                    'elasticloadbalancing:quota-loadbalancernumber')

            # save policies that were modified
            for i in range(0, len(policy_list)):
                if 'dirty' in policy_list[i].keys():
                    del policy_list[i]['dirty']
                    if user is not None:
                        view.log_request(_(u"Updating policy {0} for user {1}").format(policies.policy_names[i], user))
                        view.conn.get_response('PutUserPolicy', params={'UserName':user, 'PolicyName':policies.policy_names[i], 'PolicyDocument':json.dumps(policy_list[i]), 'DelegateAccount':as_account}, verb='POST')
                    if account is not None:
                        view.log_request(_(u"Updating policy {0} for account {1}").format(policies.policy_names[i], account))
                        view.conn.get_response('PutAccountPolicy', params={'AccountName':account, 'PolicyName':policies.policy_names[i], 'PolicyDocument':json.dumps(policy_list[i]), 'DelegateAccount':as_account}, verb='POST')
            if len(new_stmts) > 0:
                # do we already have the euca default policy?
                if self.EUCA_DEFAULT_POLICY in policies.policy_names:
                    # add the new statments in
                    default_policy = policy_list[policies.policy_names.index(self.EUCA_DEFAULT_POLICY)]
                    default_policy['Statement'].extend(new_stmts)
                    if user is not None:
                        view.log_request(_(u"Updating policy {0} for user {1}").format(self.EUCA_DEFAULT_POLICY, user))
                        view.conn.get_response('PutUserPolicy', params={'UserName':user, 'PolicyName':self.EUCA_DEFAULT_POLICY, 'PolicyDocument':json.dumps(default_policy), 'DelegateAccount':as_account}, verb='POST')
                    if account is not None:
                        view.log_request(_(u"Updating policy {0} for account {1}").format(self.EUCA_DEFAULT_POLICY, account))
                        view.conn.get_response('PutAccountPolicy', params={'AccountName':account, 'PolicyName':self.EUCA_DEFAULT_POLICY, 'PolicyDocument':json.dumps(default_policy), 'DelegateAccount':as_account}, verb='POST')
                else:
                    # create the default policy
                    new_policy = {'Version': '2011-04-01', 'Statement': new_stmts}
                    if user is not None:
                        view.log_request(_(u"Creating policy {0} for user {1}").format(self.EUCA_DEFAULT_POLICY, user))
                        view.conn.get_response('PutUserPolicy', params={'UserName':user, 'PolicyName':self.EUCA_DEFAULT_POLICY, 'PolicyDocument':json.dumps(new_policy), 'DelegateAccount':as_account}, verb='POST')
                    if account is not None:
                        view.log_request(_(u"Creating policy {0} for account {1}").format(self.EUCA_DEFAULT_POLICY, account))
                        view.conn.get_response('PutAccountPolicy', params={'AccountName':account, 'PolicyName':self.EUCA_DEFAULT_POLICY, 'PolicyDocument':json.dumps(new_policy), 'DelegateAccount':as_account}, verb='POST')

    def _update_quota_limit_(self, view, policy_list, new_stmts, param, action, condition):
        new_limit = view.request.params.get(param, '')
        lowest_val = sys.maxint
        lowest_policy = None
        lowest_policy_val = None
        lowest_stmt = None
        # scan policies to see if there's a matching condition
        for policy in policy_list:
            for s in policy['Statement']:
                try:    # skip statements without conditions
                    s['Condition']
                except KeyError:
                    continue
                for cond in s['Condition'].keys():
                    if cond == "NumericLessThanEquals": 
                        for policy_val in s['Condition'][cond].keys():
                            limit = s['Condition'][cond][policy_val]
                            # convert value to int, but if no value, set limit high
                            limit = int(limit) if limit else sys.maxint
                            if policy_val == condition:
                                # need to see if this was the policy with the lowest value.
                                if limit < lowest_val:
                                    lowest_val = limit
                                    lowest_policy = policy
                                    lowest_policy_val = policy_val
                                    lowest_stmt = s
        if lowest_val == sys.maxint: # was there a statement? If not, we should add one
            if new_limit != '':
                new_stmts.append({
                    'Effect': 'Limit', 'Action': action, 'Resource': '*',
                    'Condition': {'NumericLessThanEquals': {condition: new_limit}}
                })
        else:
            if new_limit == '' or new_limit == '0': # need to remove the value
                del lowest_stmt['Condition']['NumericLessThanEquals'][lowest_policy_val]
            else:  # need to change the value
                lowest_stmt['Condition']['NumericLessThanEquals'][lowest_policy_val] = new_limit
            lowest_policy['dirty'] = True

