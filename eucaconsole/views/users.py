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
Pyramid views for Eucalyptus and AWS Users

"""
import csv
import os
import random
import string
import StringIO
import simplejson as json
import sys

from urllib2 import HTTPError, URLError
from urllib import urlencode

from boto.exception import BotoServerError
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.users import (
    UserForm, ChangePasswordForm, GeneratePasswordForm, DeleteUserForm, AddToGroupForm, DisableUserForm, EnableUserForm)
from ..models import Notification
from ..views import BaseView, LandingPageView, JSONResponse
from . import boto_error_handler


class PasswordGeneration(object):
    @staticmethod
    def generate_password():
        """
        Generates a simple 12 character password.
        """
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'
        random.seed = (os.urandom(1024))
        return ''.join(random.choice(chars) for i in range(12))


class UsersView(LandingPageView):
    TEMPLATE = '../templates/users/users.pt'
    EUCA_DENY_POLICY = 'euca-console-deny-access-policy'

    def __init__(self, request):
        super(UsersView, self).__init__(request)
        self.initial_sort_key = 'user_name'
        self.prefix = '/users'
        self.conn = self.get_connection(conn_type="iam")

    @view_config(route_name='users', renderer=TEMPLATE)
    def users_landing(self):
        json_items_endpoint = self.request.route_path('users_json')
        if self.request.GET:
            json_items_endpoint += '?{params}'.format(params=urlencode(self.request.GET))
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['user_name', 'user_id', 'arn', 'path']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='user_name', name=_(u'User name: A to Z')),
            dict(key='-user_name', name=_(u'User name: Z to A')),
        ]

        return dict(
            filter_fields=False,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
            delete_form=DeleteUserForm(self.request),
            disable_form=DisableUserForm(self.request),
            enable_form=EnableUserForm(self.request),
        )

    @view_config(route_name='user_disable', request_method='POST', renderer='json')
    def user_disable(self):
        """ calls iam:DeleteLoginProfile and iam:PutUserPolicy """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        with boto_error_handler(self.request):
            user_name = self.request.matchdict.get('name')
            self.log_request(_(u"Disabling user {0}").format(user_name))
            result = self.conn.delete_login_profile(user_name=user_name)
            policy = {'Version': '2011-04-01'}
            statements = [{'Effect': 'Deny', 'Action': '*', 'Resource': '*'}]
            policy['Statement'] = statements
            result = self.conn.put_user_policy(user_name, self.EUCA_DENY_POLICY, json.dumps(policy))
            return dict(message=_(u"Successfully disabled user"))

    @view_config(route_name='user_enable', request_method='POST', renderer='json')
    def user_enable(self):
        """ calls iam:CreateLoginProfile and iam:DeleteUserPolicy """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        with boto_error_handler(self.request):
            user_name = self.request.matchdict.get('name')
            self.log_request(_(u"Enabling user {0}").format(user_name))
            result = self.conn.delete_user_policy(user_name, self.EUCA_DENY_POLICY)
            random_password = self.request.params.get('random_password')
            if random_password == 'y':
                password = PasswordGeneration.generate_password()
                result = self.conn.create_login_profile(user_name, password)

                # assemble file response
                account = self.request.session['account']
                string_output = StringIO.StringIO()
                csv_w = csv.writer(string_output)
                row = [account, user_name, password]
                csv_w.writerow(row)
                self._store_file_("{acct}-{user}-login.csv".format(acct=account, user=user_name),
                                  'text/csv', string_output.getvalue())
                return dict(message=_(u"Successfully added users"), results="true")
            else:
                return dict(message=_(u"Successfully enabled user"))


class UsersJsonView(BaseView):
    EUCA_DENY_POLICY = 'euca-console-deny-access-policy'

    """Users returned as JSON"""
    def __init__(self, request):
        super(UsersJsonView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")

    @view_config(route_name='users_json', renderer='json', request_method='GET')
    def users_json(self):
        users = []
        groups = []
        with boto_error_handler(self.request):
            groups = self.conn.get_all_groups()
            groups = groups.groups
            for g in groups:
                info = self.conn.get_group(group_name=g.group_name)
                g['users'] = info.users
            for user in self.get_items():
                user_groups = []
                for g in groups:
                    if user.user_name in [u.user_name for u in g.users]:
                        user_groups.append(g.group_name)
                users.append(dict(
                    path=user.path,
                    user_name=user.user_name,
                    user_id=user.user_id,
                    create_date=user.create_date,
                    num_groups=len(user_groups),
                    arn=user.arn,
                ))
            return dict(results=users)

    @view_config(route_name='user_summary_json', renderer='json', request_method='GET')
    def user_summary_json(self):
        user_param = self.request.matchdict.get('name')
        has_password = False
        try:
            profile = self.conn.get_login_profiles(user_name=user_param)
            # this call returns 404 if no password found
            has_password = True
        except BotoServerError as err:
            pass
        user_enabled = True
        try:
            if user_param != 'admin':
                policies = self.conn.get_all_user_policies(user_name=user_param)
                for policy in policies.policy_names:
                    if policy == self.EUCA_DENY_POLICY and has_password is False:
                        user_enabled = False
        except BotoServerError as err:
            pass
        keys = []
        if user_enabled: # we won't spend time fetching the keys if the user is disabled
            try:
                keys = self.conn.get_all_access_keys(user_name=user_param)
                keys = [key for key in keys.list_access_keys_result.access_key_metadata if key.status == 'Active']
            except BotoServerError as exc:
                pass

        return dict(
            results=dict(
                user_name=user_param,
                num_keys=len(keys),
                has_password=has_password,
                user_enabled=user_enabled,
            )
        )

    def get_items(self):
        with boto_error_handler(self.request):
            return self.conn.get_all_users().users


class UserView(BaseView):
    """Views for single User"""
    TEMPLATE = '../templates/users/user_view.pt'
    NEW_TEMPLATE = '../templates/users/user_new.pt'
    EUCA_DEFAULT_POLICY = 'euca-console-quota-policy'

    def __init__(self, request):
        super(UserView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        with boto_error_handler(request, request.current_route_url()):
            self.user = self.get_user()
        if self.user is None:
            self.location = self.request.route_path('users')
        else:
            self.location = self.request.route_path('user_view', name=self.user.user_name)
        self.prefix = '/users'
        self.user_form = None
        self.change_password_form = ChangePasswordForm(self.request)
        self.generate_form = GeneratePasswordForm(self.request)
        self.delete_form = DeleteUserForm(self.request)
        self.already_member_text = _(u"User already a member of all groups")
        self.no_groups_defined_text = _(u"There are no groups defined")
        self.render_dict = dict(
            user=self.user,
            prefix=self.prefix,
            user_create_date=getattr(self.user, 'create_date', None),
            change_password_form=self.change_password_form,
            generate_form=self.generate_form,
            delete_form=self.delete_form,
            disable_form=DisableUserForm(self.request),
            enable_form=EnableUserForm(self.request),
            quota_err=_(u"Requires non-negative integer (or may be empty)"),
        )

    def get_user(self):
        user_param = self.request.matchdict.get('name')
        if user_param:
            user = self.conn.get_user(user_name=user_param)
            return user
        else:
            return None

    def add_quota_limit(self, statements, param, action, condition):
        val = self.request.params.get(param, None)
        if val:
            statements.append({
                'Effect': 'Limit', 'Action': action, 'Resource': '*',
                'Condition': {'NumericLessThanEquals': {condition: val}}
            })

    @view_config(route_name='user_view', renderer=TEMPLATE)
    def user_view(self):
        if self.user is None:
            raise HTTPNotFound
        has_password = False
        try:
            profile = self.conn.get_login_profiles(user_name=self.user.user_name)
            # this call returns 404 if no password found
            has_password = True
        except BotoServerError as err:
            pass
        group_form = AddToGroupForm(self.request)
        self.render_dict['group_form'] = group_form
        self.user_form = UserForm(self.request, user=self.user, conn=self.conn, formdata=self.request.params or None)
        self.render_dict['user_form'] = self.user_form
        self.render_dict['has_password'] = 'true' if has_password else 'false'
        self.render_dict['already_member_text'] = self.already_member_text
        self.render_dict['no_groups_defined_text'] = self.no_groups_defined_text
        return self.render_dict
 
    @view_config(route_name='user_new', renderer=NEW_TEMPLATE)
    def user_new(self):
        self.user_form = UserForm(self.request, user=self.user, conn=self.conn, formdata=self.request.params or None)
        self.render_dict['user_form'] = self.user_form
        return self.render_dict
 
    @view_config(route_name='user_access_keys_json', renderer='json', request_method='GET')
    def user_keys_json(self):
        """Return user access keys list"""
        with boto_error_handler(self.request):
            keys = self.conn.get_all_access_keys(user_name=self.user.user_name)
            return dict(results=sorted(keys.list_access_keys_result.access_key_metadata))

    @view_config(route_name='user_groups_json', renderer='json', request_method='GET')
    def user_groups_json(self):
        """Return user groups list"""
        with boto_error_handler(self.request):
            groups = self.conn.get_groups_for_user(user_name=self.user.user_name)
            for g in groups.groups:
                g['title'] = g.group_name
            return dict(results=groups.groups)

    @view_config(route_name='user_avail_groups_json', renderer='json', request_method='GET')
    def user_avail_groups_json(self):
        """Return groups this user isn't part of"""
        with boto_error_handler(self.request):
            taken_groups = [
                group.group_name for group in self.conn.get_groups_for_user(user_name=self.user.user_name).groups
            ]
            all_groups = [group.group_name for group in self.conn.get_all_groups().groups]
            avail_groups = list(set(all_groups) - set(taken_groups))
            if len(avail_groups) == 0:
                if len(all_groups) == 0:
                    avail_groups.append(self.no_groups_defined_text)
                else:
                    avail_groups.append(self.already_member_text)
            return dict(results=avail_groups)

    @view_config(route_name='user_policies_json', renderer='json', request_method='GET')
    def user_policies_json(self):
        """Return user policies list"""
        if self.user.user_name == 'admin':
            return dict(results=[])
        with boto_error_handler(self.request):
            policies = self.conn.get_all_user_policies(user_name=self.user.user_name)
            return dict(results=policies.policy_names)

    @view_config(route_name='user_policy_json', renderer='json', request_method='GET')
    def user_policy_json(self):
        """Return user policies list"""
        with boto_error_handler(self.request):
            policy_name = self.request.matchdict.get('policy')
            policy = self.conn.get_user_policy(user_name=self.user.user_name, policy_name=policy_name)
            parsed = json.loads(policy.policy_document)
            return dict(results=json.dumps(parsed, indent=2))

    @view_config(route_name='user_create', renderer='json', request_method='POST')
    def user_create(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        # can't use regular form validation here. We allow empty values and the validation
        # code does not, so we need to roll our own below.
        # get user list
        users_json = self.request.params.get('users')
        # now get the rest
        random_password = self.request.params.get('random_password', 'n')
        access_keys = self.request.params.get('access_keys', 'n')
        allow_all = self.request.params.get('allow_all', 'n')
        path = self.request.params.get('path', '/')
       
        session = self.request.session
        account = session['account']
        with boto_error_handler(self.request):
            user_list = []
            if users_json:
                users = json.loads(users_json)
                for (name, email) in users.items():
                    self.log_request(_(u"Creating user {0}").format(name))
                    user = self.conn.create_user(name, path)
                    user_data = {'account': account, 'username': name}
                    policy = {'Version': '2011-04-01'}
                    statements = []
                    if random_password == 'y':
                        self.log_request(_(u"Generating password for user {0}").format(name))
                        password = PasswordGeneration.generate_password()
                        self.conn.create_login_profile(name, password)
                        user_data['password'] = password
                    if access_keys == 'y':
                        self.log_request(_(u"Creating access keys for user {0}").format(name))
                        creds = self.conn.create_access_key(name)
                        user_data['access_id'] = creds.access_key.access_key_id
                        user_data['secret_key'] = creds.access_key.secret_access_key
                    # store this away for file creation later
                    user_list.append(user_data)
                    if allow_all == 'y':
                        statements.append({'Effect': 'Allow', 'Action': '*', 'Resource': '*'})
                        statements.append({'Effect': 'Deny', 'Action': 'iam:*', 'Resource': '*'})
                    # now, look at quotas
                    ## ec2
                    self.add_quota_limit(
                        statements, 'ec2_images_max', 'ec2:RegisterImage', 'ec2:quota-imagenumber')
                    self.add_quota_limit(
                        statements, 'ec2_instances_max', 'ec2:RunInstances', 'ec2:quota-vminstancenumber')
                    self.add_quota_limit(
                        statements, 'ec2_volumes_max', 'ec2:CreateVolume', 'ec2:quota-volumenumber')
                    self.add_quota_limit(
                        statements, 'ec2_snapshots_max', 'ec2:CreateSnapshot', 'ec2:quota-snapshotnumber')
                    self.add_quota_limit(
                        statements, 'ec2_elastic_ip_max', 'ec2:AllocateAddress', 'ec2:quota-addressnumber')
                    self.add_quota_limit(
                        statements, 'ec2_total_size_all_vols', 'ec2:Createvolume', 'ec2:quota-volumetotalsize')
                    ## s3
                    self.add_quota_limit(
                        statements, 's3_buckets_max', 's3:CreateBucket', 's3:quota-bucketnumber')
                    self.add_quota_limit(
                        statements, 's3_objects_per__max', 's3:CreateObject', 's3:quota-bucketobjectnumber')
                    self.add_quota_limit(
                        statements, 's3_bucket_size', 's3:PutObject', 's3:quota-bucketsize')
                    self.add_quota_limit(
                        statements, 's3_total_size_all_buckets', 's3:pubobject', 's3:quota-buckettotalsize')
                    ## iam
                    self.add_quota_limit(
                        statements, 'iam_groups_max', 'iam:CreateGroup', 'iam:quota-groupnumber')
                    self.add_quota_limit(
                        statements, 'iam_users_max', 'iam:CreateUser', 'iam:quota-usernumber')
                    self.add_quota_limit(
                        statements, 'iam_roles_max', 'iam:CreateRole', 'iam:quota-rolenumber')
                    self.add_quota_limit(
                        statements, 'iam_inst_profiles_max',
                        'iam:CreateInstanceProfile', 'iam:quota-instanceprofilenumber')
                    ## autoscaling
                    self.add_quota_limit(
                        statements, 'autoscale_groups_max', 'autoscaling:createautoscalinggroup',
                        'autoscaling:quota-autoscalinggroupnumber')
                    self.add_quota_limit(
                        statements, 'launch_configs_max', 'autoscaling:createlaunchconfiguration',
                        'autoscaling:quota-launchconfigurationnumber')
                    self.add_quota_limit(
                        statements, 'scaling_policies_max', 'autoscaling:pubscalingpolicy',
                        'autoscaling:quota-scalingpolicynumber')
                    ## elb
                    self.add_quota_limit(
                        statements, 'elb_load_balancers_max', 'elasticloadbalancing:createloadbalancer',
                        'elasticloadbalancing:quota-loadbalancernumber')

                    if len(statements) > 0:
                        self.log_request(_(u"Creating policy for user {0}").format(name))
                        policy['Statement'] = statements
                        self.conn.put_user_policy(name, self.EUCA_DEFAULT_POLICY, json.dumps(policy))
            # create file to send instead. Since # users is probably small, do it all in memory
            has_file = 'n'
            if not (access_keys == 'n' and random_password == 'n'):
                string_output = StringIO.StringIO()
                csv_w = csv.writer(string_output)
                for user in user_list:
                    row = [user['account'], user['username']]
                    if random_password == 'y':
                        row.append(user['password'])
                    if access_keys == 'y':
                        row.append(user['access_id'])
                        row.append(user['secret_key'])
                    csv_w.writerow(row)
                self._store_file_("{acct}-users.csv".format(acct=account), 'text/csv', string_output.getvalue())
                has_file = 'y'
            return dict(message=_(u"Successfully added users"), results=dict(hasFile=has_file))
 
    @view_config(route_name='user_update', request_method='POST', renderer='json')
    def user_update(self):
        """ calls iam:UpdateUser """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        with boto_error_handler(self.request):
            new_name = self.request.params.get('user_name', None)
            path = self.request.params.get('path', None)
            self.log_request(_(u"Updating user {0} (new_name={1}, path={2})").format(self.user.user_name, new_name, path))
            if new_name == self.user.user_name:
                new_name = None
            result = self.conn.update_user(user_name=self.user.user_name, new_user_name=new_name, new_path=path)
            self.user.path = path
            if self.user.user_name != new_name:
                pass  # TODO: need to force view refresh if name changes
            return dict(message=_(u"Successfully updated user information"),
                        results=self.user)

    @view_config(route_name='user_change_password', request_method='POST', renderer='json')
    def user_change_password(self):
        """ calls iam:UpdateLoginProfile """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        try:
            password = self.request.params.get('password')
            new_pass = self.request.params.get('new_password')

            auth = self.get_connection(conn_type='sts')
            session = self.request.session
            account = session['account']
            username = session['username']
            # 900 is minimum duration for session creds
            creds = auth.authenticate(account=account, user=username, passwd=password, timeout=8, duration=900)
            self.log_request(_(u"Change password for user {0}").format(self.user.user_name))
            try:
                # try to fetch login profile.
                self.conn.get_login_profiles(user_name=self.user.user_name)
                # if that worked, update the profile
                result = self.conn.update_login_profile(user_name=self.user.user_name, password=new_pass)
            except BotoServerError:
                # if that failed, create the profile
                result = self.conn.create_login_profile(user_name=self.user.user_name, password=new_pass)
            # assemble file response
            account = self.request.session['account']
            string_output = StringIO.StringIO()
            csv_w = csv.writer(string_output)
            row = [account, self.user.user_name, new_pass]
            csv_w.writerow(row)
            self._store_file_("{acct}-{user}-login.csv".format(
                acct=account, user=self.user.user_name), 'text/csv', string_output.getvalue())
            return dict(message=_(u"Successfully set user password"), results="true")
        except BotoServerError as err:  # catch error in password change
            return BaseView.handle_error(err)
        except HTTPError, err:          # catch error in authentication
            if err.msg == 'Unauthorized':
                err.msg = _(u"The password you entered is incorrect.")
            return JSONResponse(status=401, message=err.msg)
        except URLError, err:           # catch error in authentication
            return JSONResponse(status=401, message=err.msg)

    @view_config(route_name='user_random_password', request_method='POST', renderer='json')
    def user_random_password(self):
        """ calls iam:UpdateLoginProfile """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        with boto_error_handler(self.request):
            new_pass = PasswordGeneration.generate_password()
            self.log_request(_(u"Generating password for user {0}").format(self.user.user_name))
            try:
                # try to fetch login profile.
                self.conn.get_login_profiles(user_name=self.user.user_name)
                # if that worked, update the profile
                result = self.conn.update_login_profile(user_name=self.user.user_name, password=new_pass)
            except BotoServerError:
                # if that failed, create the profile
                result = self.conn.create_login_profile(user_name=self.user.user_name, password=new_pass)
            # assemble file response
            account = self.request.session['account']
            string_output = StringIO.StringIO()
            csv_w = csv.writer(string_output)
            row = [account, self.user.user_name, new_pass]
            csv_w.writerow(row)
            self._store_file_(
                "{acct}-{user}-login.csv".format(acct=account, user=self.user.user_name),
                'text/csv', string_output.getvalue())
            return dict(message=_(u"Successfully generated user password"), results="true")

    @view_config(route_name='user_delete_password', request_method='POST', renderer='json')
    def user_delete_password(self):
        """ calls iam:DeleteLoginProfile """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        with boto_error_handler(self.request):
            self.log_request(_(u"Deleting password for user {0}").format(self.user.user_name))
            self.conn.delete_login_profile(user_name=self.user.user_name)
            return dict(message=_(u"Successfully deleted user password"), results="true")

    @view_config(route_name='user_generate_keys', request_method='POST', renderer='json')
    def user_gen_keys(self):
        """ calls iam:CreateAccessKey """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        with boto_error_handler(self.request):
            self.log_request(_(u"Creating access keys for user {0}").format(self.user.user_name))
            result = self.conn.create_access_key(user_name=self.user.user_name)
            account = self.request.session['account']
            string_output = StringIO.StringIO()
            csv_w = csv.writer(string_output)
            row = [account, self.user.user_name, result.access_key.access_key_id, result.access_key.secret_access_key]
            csv_w.writerow(row)
            self._store_file_(
                "{acct}-{user}-{key}-creds.csv".format(acct=account,
                user=self.user.user_name, key=result.access_key.access_key_id),
                'text/csv', string_output.getvalue())
            return dict(message=_(u"Successfully generated access keys"), results="true")

    @view_config(route_name='user_delete_key', request_method='POST', renderer='json')
    def user_delete_key(self):
        """ calls iam:DeleteAccessKey """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        key_id = self.request.matchdict.get('key')
        with boto_error_handler(self.request):
            self.log_request(_(u"Deleting access key {0} for user {1}").format(key_id, self.user.user_name))
            result = self.conn.delete_access_key(user_name=self.user.user_name, access_key_id=key_id)
            return dict(message=_(u"Successfully deleted key"))

    @view_config(route_name='user_deactivate_key', request_method='POST', renderer='json')
    def user_deactivate_key(self):
        """ calls iam:UpdateAccessKey """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        key_id = self.request.matchdict.get('key')
        with boto_error_handler(self.request):
            self.log_request(_(u"Deactivating access key {0} for user {1}").format(key_id, self.user.user_name))
            result = self.conn.update_access_key(user_name=self.user.user_name, access_key_id=key_id, status="Inactive")
            return dict(message=_(u"Successfully deactivated key"))

    @view_config(route_name='user_activate_key', request_method='POST', renderer='json')
    def user_activate_key(self):
        """ calls iam:UpdateAccessKey """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        key_id = self.request.matchdict.get('key')
        with boto_error_handler(self.request):
            self.log_request(_(u"Activating access key {0} for user {1}").format(key_id, self.user.user_name))
            result = self.conn.update_access_key(user_name=self.user.user_name, access_key_id=key_id, status="Active")
            return dict(message=_(u"Successfully activated key"))

    @view_config(route_name='user_add_to_group', request_method='POST', renderer='json')
    def user_add_to_group(self):
        """ calls iam:AddUserToGroup """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        group = self.request.matchdict.get('group')
        with boto_error_handler(self.request):
            self.log_request(_(u"Adding user {0} to group {1}").format(self.user.user_name, group))
            result = self.conn.add_user_to_group(user_name=self.user.user_name, group_name=group)
            return dict(message=_(u"Successfully added user to group"),
                        results=result)

    @view_config(route_name='user_remove_from_group', request_method='POST', renderer='json')
    def user_remove_from_group(self):
        """ calls iam:RemoveUserToGroup """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        group = self.request.matchdict.get('group')
        with boto_error_handler(self.request):
            self.log_request(_(u"Removing user {0} from group {1}").format(self.user.user_name, group))
            result = self.conn.remove_user_from_group(user_name=self.user.user_name, group_name=group)
            return dict(message=_(u"Successfully removed user from group"),
                        results=result)

    @view_config(route_name='user_delete', request_method='POST')
    def user_delete(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        if self.user is None:
            raise HTTPNotFound
        with boto_error_handler(self.request):
            self.log_request(_(u"Deleting user {0}").format(self.user.user_name))
            params = {'UserName': self.user.user_name, 'IsRecursive': 'true'}
            self.conn.get_response('DeleteUser', params)
            
            location = self.request.route_path('users')
            msg = _(u'Successfully deleted user')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

    @view_config(route_name='user_update_policy', request_method='POST', renderer='json')
    def user_update_policy(self):
        """ calls iam:PutUserPolicy """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        policy = str(self.request.matchdict.get('policy'))
        with boto_error_handler(self.request):
            self.log_request(_(u"Updating policy {0} for user {1}").format(policy, self.user.user_name))
            policy_text = self.request.params.get('policy_text')
            result = self.conn.put_user_policy(
                user_name=self.user.user_name, policy_name=policy, policy_json=policy_text)
            return dict(message=_(u"Successfully updated user policy"), results=result)

    @view_config(route_name='user_delete_policy', request_method='POST', renderer='json')
    def user_delete_policy(self):
        """ calls iam:DeleteUserPolicy """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        policy = self.request.matchdict.get('policy')
        with boto_error_handler(self.request):
            self.log_request(_(u"Deleting policy {0} for user {1}").format(policy, self.user.user_name))
            result = self.conn.delete_user_policy(user_name=self.user.user_name, policy_name=policy)
            return dict(message=_(u"Successfully deleted user policy"), results=result)

    @view_config(route_name='user_update_quotas', request_method='POST', renderer='json')
    def user_update_quotas(self):
        """ calls iam:PutUserPolicy """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        if self.user is None:
            raise HTTPNotFound
        with boto_error_handler(self.request):
            # load all policies for this user
            policy_list = []
            policies = self.conn.get_all_user_policies(user_name=self.user.user_name)
            for policy_name in policies.policy_names:
                policy_json = self.conn.get_user_policy(
                    user_name=self.user.user_name, policy_name=policy_name).policy_document
                policy = json.loads(policy_json)
                policy_list.append(policy)
            # for each form item, update proper policy if needed
            new_stmts = []
            ## ec2
            self.update_quota_limit(policy_list, new_stmts,
                                    'ec2_images_max', 'ec2:RegisterImage', 'ec2:quota-imagenumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'ec2_instances_max', 'ec2:RunInstances', 'ec2:quota-vminstancenumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'ec2_volumes_max', 'ec2:CreateVolume', 'ec2:quota-volumenumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'ec2_snapshots_max', 'ec2:CreateSnapshot', 'ec2:quota-snapshotnumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'ec2_elastic_ip_max', 'ec2:AllocateAddress', 'ec2:quota-addressnumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'ec2_total_size_all_vols', 'ec2:Createvolume', 'ec2:quota-volumetotalsize')
            ## s3
            self.update_quota_limit(policy_list, new_stmts,
                                    's3_buckets_max', 's3:CreateBucket', 's3:quota-bucketnumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    's3_objects_per__max', 's3:CreateObject', 's3:quota-bucketobjectnumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    's3_bucket_size', 's3:PutObject', 's3:quota-bucketsize')
            self.update_quota_limit(policy_list, new_stmts,
                                    's3_total_size_all_buckets', 's3:pubobject', 's3:quota-buckettotalsize')
            ## iam
            self.update_quota_limit(policy_list, new_stmts,
                                    'iam_groups_max', 'iam:CreateGroup', 'iam:quota-groupnumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'iam_users_max', 'iam:CreateUser', 'iam:quota-usernumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'iam_roles_max', 'iam:CreateRole', 'iam:quota-rolenumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'iam_inst_profiles_max', 'iam:CreateInstanceProfile',
                                    'iam:quota-instanceprofilenumber')
            ## autoscaling
            self.update_quota_limit(policy_list, new_stmts,
                                    'autoscale_groups_max', 'autoscaling:createautoscalinggroup',
                                    'autoscaling:quota-autoscalinggroupnumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'launch_configs_max', 'autoscaling:createlaunchconfiguration',
                                    'autoscaling:quota-launchconfigurationnumber')
            self.update_quota_limit(policy_list, new_stmts,
                                    'scaling_policies_max', 'autoscaling:pubscalingpolicy',
                                    'autoscaling:quota-scalingpolicynumber')
            ## elb
            self.update_quota_limit(policy_list, new_stmts,
                                    'elb_load_balancers_max', 'elasticloadbalancing:createloadbalancer',
                                    'elasticloadbalancing:quota-loadbalancernumber')

            # save policies that were modified
            for i in range(0, len(policy_list)):
                if 'dirty' in policy_list[i].keys():
                    del policy_list[i]['dirty']
                    self.log_request(_(u"Updating policy {0} for user {1}").format(
                        policies.policy_names[i], self.user.user_name))
                    self.conn.put_user_policy(
                        self.user.user_name, policies.policy_names[i], json.dumps(policy_list[i]))
            if len(new_stmts) > 0:
                # do we already have the euca default policy?
                if self.EUCA_DEFAULT_POLICY in policies.policy_names:
                    # add the new statments in
                    self.log_request(_(u"Updating policy {0} for user {1}").format(
                        self.EUCA_DEFAULT_POLICY, self.user.user_name))
                    default_policy = policy_list[policies.policy_names.index(self.EUCA_DEFAULT_POLICY)]
                    default_policy['Statement'].extend(new_stmts)
                    self.conn.put_user_policy(self.user.user_name, self.EUCA_DEFAULT_POLICY, json.dumps(default_policy))
                else:
                    # create the default policy
                    self.log_request(_(u"Creating policy {0} for user {1}").format(
                        self.EUCA_DEFAULT_POLICY, self.user.user_name))
                    new_policy = {'Version': '2011-04-01', 'Statement': new_stmts}
                    self.conn.put_user_policy(self.user.user_name, self.EUCA_DEFAULT_POLICY, json.dumps(new_policy))
            return dict(message=_(u"Successfully updated user policy"))

    def update_quota_limit(self, policy_list, new_stmts, param, action, condition):
        new_limit = self.request.params.get(param, '')
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
            if new_limit == '': # need to remove the value
                del lowest_stmt['Condition']['NumericLessThanEquals'][lowest_policy_val]
            else:  # need to change the value
                lowest_stmt['Condition']['NumericLessThanEquals'][lowest_policy_val] = new_limit
            lowest_policy['dirty'] = True

