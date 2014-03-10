# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Users

"""
import csv
from dateutil import parser
import os
import random
import string
import StringIO
import simplejson as json
import sys
import urlparse

from urllib2 import HTTPError, URLError
from urllib import urlencode

from boto.exception import BotoServerError
from boto.exception import EC2ResponseError
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config
from pyramid.response import Response

from ..forms.users import UserForm, ChangePasswordForm, GeneratePasswordForm, DeleteUserForm, AddToGroupForm, DisableUserForm, EnableUserForm
from ..models import Notification
from ..views import BaseView, LandingPageView, JSONResponse
from ..models.auth import EucaAuthenticator


class PasswordGeneration(object):
    @staticmethod
    def generatePassword():
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

    @view_config(route_name='users', renderer=TEMPLATE)
    def users_landing(self):
        json_items_endpoint = self.request.route_url('users_json')
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
        self.conn = self.get_connection(conn_type="iam")
        try:
            user_name = self.request.matchdict.get('name')
            result = self.conn.delete_login_profile(user_name=user_name)
            policy = {}
            policy['Version'] = '2011-04-01'
            statements = []
            statements.append({'Effect': 'Deny', 'Action': '*', 'Resource': '*'})
            policy['Statement'] = statements
            result = self.conn.put_user_policy(user_name, self.EUCA_DENY_POLICY, json.dumps(policy))
            return dict(message=_(u"Successfully disabled user"))
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_enable', request_method='POST', renderer='json')
    def user_enable(self):
        """ calls iam:CreateLoginProfile and iam:DeleteUserPolicy """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        self.conn = self.get_connection(conn_type="iam")
        try:
            user_name = self.request.matchdict.get('name')
            result = self.conn.delete_user_policy(user_name, self.EUCA_DENY_POLICY)
            random_password = self.request.params.get('random_password')
            if random_password == 'y':
                password = PasswordGeneration.generatePassword()
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
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

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
        try:
            groups = self.conn.get_all_groups()
            groups = groups.groups
            for g in groups:
                info = self.conn.get_group(group_name=g.group_name)
                g['users'] = info.users
        except EC2ResponseError as exc:
            pass
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
        user = self.conn.get_user(user_name=user_param)
        has_password = False
        try:
            profile = self.conn.get_login_profiles(user_name=user.user_name)
            # this call returns 404 if no password found
            has_password = True
        except BotoServerError as err:
            pass
        user_enabled = True
        try:
            policies = self.conn.get_all_user_policies(user_name=user.user_name)
            for policy in policies.policy_names:
                if policy == self.EUCA_DENY_POLICY and has_password is False:
                    user_enabled = False
        except BotoServerError as err:
            pass
        keys = []
        if user_enabled: # we won't spend time fetching the keys if the user is disabled
            try:
                keys = self.conn.get_all_access_keys(user_name=user.user_name)
                keys = [key for key in keys.list_access_keys_result.access_key_metadata if key.status == 'Active']
            except EC2ResponseError as exc:
                pass

        return dict(results=dict(
                user_name=user.user_name,
                num_keys=len(keys),
                has_password=has_password,
                user_enabled=user_enabled,
            ))

    def get_items(self):
        try:
            return self.conn.get_all_users().users
        except BotoServerError as exc:
            return BaseView.handle_403_error(exc, request=self.request)


class UserView(BaseView):
    """Views for single User"""
    TEMPLATE = '../templates/users/user_view.pt'
    NEW_TEMPLATE = '../templates/users/user_new.pt'
    EUCA_DEFAULT_POLICY = 'euca-console-quota-policy'

    def __init__(self, request):
        super(UserView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        self.user = self.get_user()
        if self.user is None:
            self.location = self.request.route_url('users')
        else:
            self.location = self.request.route_url('user_view', name=self.user.user_name)
        self.prefix = '/users'
        self.user_form = None
        self.change_password_form = ChangePasswordForm(self.request)
        self.generate_form = GeneratePasswordForm(self.request)
        self.delete_form = DeleteUserForm(self.request)
        create_date = parser.parse(self.user.create_date)
        self.render_dict = dict(
            user=self.user,
            prefix=self.prefix,
            user_create_date=create_date,
            change_password_form=self.change_password_form,
            generate_form=self.generate_form,
            delete_form=self.delete_form,
        )

    def get_user(self):
        user_param = self.request.matchdict.get('name')
        if user_param:
            user = self.conn.get_user(user_name=user_param)
            return user
        else:
            return None

    def addQuotaLimit(self, statements, param, action, condition):
        val = self.request.params.get(param, None)
        if val:
            statements.append({'Effect': 'Limit', 'Action': action,
                'Resource': '*', 'Condition':{'NumericLessThanEquals':{condition: val}}})

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
        self.user_form = UserForm(self.request, user=self.user, conn=self.conn,
                             formdata=self.request.params or None)
        self.render_dict['user_form'] = self.user_form
        self.render_dict['has_password'] = 'true' if has_password else 'false'
        return self.render_dict
 
    @view_config(route_name='user_new', renderer=NEW_TEMPLATE)
    def user_new(self):
        self.user_form = UserForm(self.request, user=self.user, conn=self.conn,
                             formdata=self.request.params or None)
        self.render_dict['user_form'] = self.user_form
        return self.render_dict
 
    @view_config(route_name='user_access_keys_json', renderer='json', request_method='GET')
    def user_keys_json(self):
        """Return user access keys list"""
        keys = self.conn.get_all_access_keys(user_name=self.user.user_name)
        return dict(results=sorted(keys.list_access_keys_result.access_key_metadata))

    @view_config(route_name='user_groups_json', renderer='json', request_method='GET')
    def user_groups_json(self):
        """Return user groups list"""
        groups = self.conn.get_groups_for_user(user_name=self.user.user_name)
        for g in groups.groups:
            g['title'] = g.group_name
        return dict(results=groups.groups)

    @view_config(route_name='user_avail_groups_json', renderer='json', request_method='GET')
    def user_avail_groups_json(self):
        """Return groups this user isn't part of"""
        taken_groups = [group.group_name for group in self.conn.get_groups_for_user(user_name=self.user.user_name).groups]
        all_groups = [group.group_name for group in self.conn.get_all_groups().groups]
        avail_groups = list(set(all_groups) - set(taken_groups))
        if len(avail_groups) == 0:
            avail_groups.append(_(u"User already a member of all groups"))
        return dict(results=avail_groups)

    @view_config(route_name='user_policies_json', renderer='json', request_method='GET')
    def user_policies_json(self):
        """Return user policies list"""
        policies = self.conn.get_all_user_policies(user_name=self.user.user_name)
        return dict(results=policies.policy_names)

    @view_config(route_name='user_policy_json', renderer='json', request_method='GET')
    def user_policy_json(self):
        """Return user policies list"""
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
        account=session['account']
        try:
            user_list = []
            if users_json:
                users = json.loads(users_json)
                for (name, email) in users.items():
                    user = self.conn.create_user(name, path)
                    user_data = {'account': account, 'username':name}
                    policy = {}
                    policy['Version'] = '2011-04-01'
                    statements = []
                    if random_password == 'y':
                        password = PasswordGeneration.generatePassword()
                        self.conn.create_login_profile(name, password)
                        user_data['password'] = password
                    if access_keys == 'y':
                        creds = self.conn.create_access_key(name)
                        user_data['access_id'] = creds.access_key.access_key_id
                        user_data['secret_key'] = creds.access_key.secret_access_key
                    # store this away for file creation later
                    user_list.append(user_data)
                    if allow_all == 'y':
                        statements.append({'Effect': 'Allow', 'Action': '*', 'Resource': '*'})
                    # now, look at quotas
                    ## ec2
                    self.addQuotaLimit(statements,
                        'ec2_images_max', 'ec2:RegisterImage', 'ec2:quota-imagenumber')
                    self.addQuotaLimit(statements,
                        'ec2_instances_max', 'ec2:RunInstances', 'ec2:quota-vminstancenumber')
                    self.addQuotaLimit(statements,
                        'ec2_volumes_max', 'ec2:CreateVolume', 'ec2:quota-volumenumber')
                    self.addQuotaLimit(statements,
                        'ec2_snapshots_max', 'ec2:CreateSnapshot', 'ec2:quota-snapshotnumber')
                    self.addQuotaLimit(statements,
                        'ec2_elastic_ip_max', 'ec2:AllocateAddress', 'ec2:quota-addressnumber')
                    self.addQuotaLimit(statements,
                        'ec2_total_size_all_vols', 'ec2:createvolume', 'ec2:quota-volumetotalsize')
                    ## s3
                    self.addQuotaLimit(statements,
                        's3_buckets_max', 's3:CreateBucket', 's3:quota-bucketnumber')
                    self.addQuotaLimit(statements,
                        's3_objects_per__max', 's3:CreateObject', 's3:quota-bucketobjectnumber')
                    self.addQuotaLimit(statements,
                        's3_bucket_size', 's3:PutObject', 's3:quota-bucketsize')
                    self.addQuotaLimit(statements,
                        's3_total_size_all_buckets', 's3:pubobject', 's3:quota-buckettotalsize')
                    ## iam
                    self.addQuotaLimit(statements,
                        'iam_groups_max', 'iam:CreateGroup', 'iam:quota-groupnumber')
                    self.addQuotaLimit(statements,
                        'iam_users_max', 'iam:CreateUser', 'iam:quota-usernumber')
                    self.addQuotaLimit(statements,
                        'iam_roles_max', 'iam:CreateRole', 'iam:quota-rolenumber')
                    self.addQuotaLimit(statements,
                        'iam_inst_profiles_max', 'iam:CreateInstanceProfile', 'iam:quota-instanceprofilenumber')
                    ## autoscaling
                    self.addQuotaLimit(statements,
                        'autoscale_groups_max', 'autoscaling:createautoscalinggroup', 'autoscaling:quota-autoscalinggroupnumber')
                    self.addQuotaLimit(statements,
                        'launch_configs_max', 'autoscaling:createlaunchconfiguration', 'autoscaling:quota-launchconfigurationnumber')
                    self.addQuotaLimit(statements,
                        'scaling_policies_max', 'autoscaling:pubscalingpolicy', 'autoscaling:quota-scalingpolicynumber')
                    ## elb
                    self.addQuotaLimit(statements,
                        'elb_load_balancers_max', 'elasticloadbalancing:createloadbalancer', 'elasticloadbalancing:quota-loadbalancernumber')

                    if len(statements) > 0:
                        policy['Statement'] = statements
                        self.conn.put_user_policy(name, self.EUCA_DEFAULT_POLICY, json.dumps(policy))
            # create file to send instead. Since # users is probably small, do it all in memory
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
            self._store_file_("{acct}-users.csv".format(acct=account),
                        'text/csv', string_output.getvalue())
            return dict(message=_(u"Successfully added users"), results="true")
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message)
 
    @view_config(route_name='user_update', request_method='POST', renderer='json')
    def user_update(self):
        """ calls iam:UpdateUser """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        try:
            new_name = self.request.params.get('user_name', None)
            path = self.request.params.get('path', None)
            if new_name == self.user.user_name:
                new_name = None
            result = self.conn.update_user(user_name=self.user.user_name, new_user_name=new_name, new_path=path)
            self.user.path = path;
            if self.user.user_name != new_name:
                pass # TODO: need to force view refresh if name changes
            return dict(message=_(u"Successfully updated user information"),
                        results=self.user)
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_change_password', request_method='POST', renderer='json')
    def user_change_password(self):
        """ calls iam:UpdateLoginProfile """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        try:
            password = self.request.params.get('password')
            new_pass = self.request.params.get('new_password')

            clchost = self.request.registry.settings.get('clchost')
            duration = str(int(self.request.registry.settings.get('session.cookie_expires'))+60)
            auth = EucaAuthenticator(host=clchost, duration=duration)
            session = self.request.session
            account=session['account']
            username=session['username']
            creds = auth.authenticate(account=account, user=username,
                                      passwd=password, timeout=8)
            # store new token values in session
            session['session_token'] = creds.session_token
            session['access_id'] = creds.access_key
            session['secret_key'] = creds.secret_key
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
            self._store_file_("{acct}-{user}-login.csv".format(acct=account, user=self.user.user_name),
                        'text/csv', string_output.getvalue())
            return dict(message=_(u"Successfully set user password"), results="true")
        except BotoServerError as err:  # catch error in password change
            return JSONResponse(status=400, message=err.message);
        except HTTPError, err:          # catch error in authentication
            return JSONResponse(status=401, message=err.msg);
        except URLError, err:           # catch error in authentication
            return JSONResponse(status=401, message=err.msg);

    @view_config(route_name='user_random_password', request_method='POST', renderer='json')
    def user_random_password(self):
        """ calls iam:UpdateLoginProfile """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        try:
            new_pass = PasswordGeneration.generatePassword()
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
            self._store_file_("{acct}-{user}-login.csv".format(acct=account, user=self.user.user_name),
                        'text/csv', string_output.getvalue())
            return dict(message=_(u"Successfully generated user password"), results="true")
        except BotoServerError as err:  # catch error in password change
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_delete_password', request_method='POST', renderer='json')
    def user_delete_password(self):
        """ calls iam:DeleteLoginProfile """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        try:
            self.conn.delete_login_profile(user_name=self.user.user_name)
            return dict(message=_(u"Successfully deleted user password"), results="true")
        except BotoServerError as err:  # catch error in password delete
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_generate_keys', request_method='POST', renderer='json')
    def user_genKeys(self):
        """ calls iam:CreateAccessKey """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        try:
            result = self.conn.create_access_key(user_name=self.user.user_name)
            account = self.request.session['account']
            string_output = StringIO.StringIO()
            csv_w = csv.writer(string_output)
            row = [account, self.user.user_name, result.access_key.access_key_id, result.access_key.secret_access_key]
            csv_w.writerow(row)
            self._store_file_("{acct}-{user}-{key}-creds.csv".format(acct=account, \
                        user=self.user.user_name, key=result.access_key.access_key_id),
                        'text/csv', string_output.getvalue())
            return dict(message=_(u"Successfully generated access keys"), results="true")
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_delete_key', request_method='POST', renderer='json')
    def user_delete_key(self):
        """ calls iam:DeleteAccessKey """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        key_id = self.request.matchdict.get('key')
        try:
            result = self.conn.delete_access_key(user_name=self.user.user_name, access_key_id=key_id)
            return dict(message=_(u"Successfully deleted key"))
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_deactivate_key', request_method='POST', renderer='json')
    def user_deactivate_key(self):
        """ calls iam:UpdateAccessKey """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        key_id = self.request.matchdict.get('key')
        try:
            result = self.conn.update_access_key(user_name=self.user.user_name, access_key_id=key_id, status="Inactive")
            return dict(message=_(u"Successfully deactivated key"))
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_activate_key', request_method='POST', renderer='json')
    def user_activate_key(self):
        """ calls iam:UpdateAccessKey """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        key_id = self.request.matchdict.get('key')
        try:
            result = self.conn.update_access_key(user_name=self.user.user_name, access_key_id=key_id, status="Active")
            return dict(message=_(u"Successfully activated key"))
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_add_to_group', request_method='POST', renderer='json')
    def user_add_to_group(self):
        """ calls iam:AddUserToGroup """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        group = self.request.matchdict.get('group')
        try:
            result = self.conn.add_user_to_group(user_name=self.user.user_name, group_name=group)
            return dict(message=_(u"Successfully added user to group"),
                        results=result)
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_remove_from_group', request_method='POST', renderer='json')
    def user_remove_from_group(self):
        """ calls iam:RemoveUserToGroup """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        group = self.request.matchdict.get('group')
        try:
            result = self.conn.remove_user_from_group(user_name=self.user.user_name, group_name=group)
            return dict(message=_(u"Successfully removed user to group"),
                        results=result)
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

    @view_config(route_name='user_delete', request_method='POST')
    def user_delete(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        if self.user is None:
            raise HTTPNotFound
        try:
            params = {'UserName': self.user.user_name, 'IsRecursive': 'true'}
            self.conn.get_response('DeleteUser', params)
            
            location = self.request.route_url('users')
            msg = _(u'Successfully deleted user')
            queue = Notification.SUCCESS
        except BotoServerError as err:
            location = self.location
            msg = err.message
            queue = Notification.ERROR
        self.request.session.flash(msg, queue=queue)
        return HTTPFound(location=location)

    @view_config(route_name='user_update_policy', request_method='POST', renderer='json')
    def user_update_policy(self):
        """ calls iam:PutUserPolicy """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        policy = str(self.request.matchdict.get('policy'))
        try:
            policy_text = self.request.params.get('policy_text')
            result = self.conn.put_user_policy(
                user_name=self.user.user_name, policy_name=policy, policy_json=policy_text)
            return dict(message=_(u"Successfully updated user policy"), results=result)
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message)

    @view_config(route_name='user_delete_policy', request_method='POST', renderer='json')
    def user_delete_policy(self):
        """ calls iam:DeleteUserPolicy """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        policy = self.request.matchdict.get('policy')
        try:
            result = self.conn.delete_user_policy(user_name=self.user.user_name, policy_name=policy)
            return dict(message=_(u"Successfully deleted user policy"), results=result)
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message)

    @view_config(route_name='user_update_quotas', request_method='POST', renderer='json')
    def user_update_quotas(self):
        """ calls iam:PutUserPolicy """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        if self.user is None:
            raise HTTPNotFound
        try:
            # load all policies for this user
            policy_list = []
            policies = self.conn.get_all_user_policies(user_name=self.user.user_name)
            for policy_name in policies.policy_names:
                policy_json = self.conn.get_user_policy(user_name=self.user.user_name,
                                    policy_name=policy_name).policy_document
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
                'ec2_total_size_all_vols', 'ec2:createvolume', 'ec2:quota-volumetotalsize')
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
                'iam_inst_profiles_max', 'iam:CreateInstanceProfile', 'iam:quota-instanceprofilenumber')
            ## autoscaling
            self.update_quota_limit(policy_list, new_stmts,
                'autoscale_groups_max', 'autoscaling:createautoscalinggroup', 'autoscaling:quota-autoscalinggroupnumber')
            self.update_quota_limit(policy_list, new_stmts,
                'launch_configs_max', 'autoscaling:createlaunchconfiguration', 'autoscaling:quota-launchconfigurationnumber')
            self.update_quota_limit(policy_list, new_stmts,
                'scaling_policies_max', 'autoscaling:pubscalingpolicy', 'autoscaling:quota-scalingpolicynumber')
            ## elb
            self.update_quota_limit(policy_list, new_stmts,
                'elb_load_balancers_max', 'elasticloadbalancing:createloadbalancer', 'elasticloadbalancing:quota-loadbalancernumber')

            # save policies that were modified
            for i in range(0, len(policy_list)-1):
                if 'dirty' in policy_list[i].keys():
                    del policy_list[i]['dirty']
                    self.conn.put_user_policy(self.user.user_name, policies.policies_names[i],
                                              json.dumps(policy_list[i]))
            if len(new_stmts) > 0:
                # do we already have the euca default policy?
                if self.EUCA_DEFAULT_POLICY in policies:
                    # add the new statments in
                    default_policy = policy_list[policies.indexOf(self.EUCA_DEFAULT_POLICY)]
                    default_policy['Statement'].extend(new_stmts)
                    self.conn.put_user_policy(self.user.user_name, self.EUCA_DEFAULT_POLICY,
                                              json.dumps(default_policy))
                else:
                    # create the default policy
                    new_policy = {}
                    new_policy['Version'] = '2011-04-01'
                    new_policy['Statement'] = new_stmts
                    self.conn.put_user_policy(self.user.user_name, self.EUCA_DEFAULT_POLICY,
                                              json.dumps(new_policy))
            return dict(message=_(u"Successfully updated user policy"))
        except BotoServerError as err:
            return JSONResponse(status=400, message=err.message);

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
                            if policy_val == condition:
                                # need to see if this was the policy with the lowest value.
                                if limit < lowest_val:
                                    lowest_val = limit
                                    lowest_policy = policy
                                    lowest_policy_val = policy_val
                                    lowest_stmt = s
        if lowest_val == sys.maxint: # was there a statement? If not, we should add one
            if new_limit != '':
                new_stmts.append({'Effect': 'Limit', 'Action': action,
                    'Resource': '*', 'Condition':{'NumericLessThanEquals':{condition: new_limit}}})
        else:
            if new_limit != '': # need to remove the value
                del lowest_stmt['Condition']['NumericLessThanEquals'][lowest_policy_val]
            else: # need to change the value
                lowest_stmt['Condition']['NumericLessThanEquals'][lowest_policy_val] = new_limit
            lowest_policy['dirty'] = True

