# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Users

"""
import os, random, string
from urllib2 import HTTPError, URLError
from urllib import urlencode
import simplejson as json

from boto.exception import BotoServerError
from pyramid.httpexceptions import exception_response
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config


from ..forms.users import UserForm, ChangePasswordForm, DeleteUserForm
from ..models import Notification
from ..models import LandingPageFilter
from ..views import BaseView, LandingPageView, TaggedItemView
from ..models.auth import EucaAuthenticator


class UsersView(LandingPageView):
    TEMPLATE = '../templates/users/users.pt'

    def __init__(self, request):
        super(UsersView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/users'

    @view_config(route_name='users', renderer=TEMPLATE)
    def users_landing(self):
        json_items_endpoint = self.request.route_url('users_json')
        if self.request.GET:
            json_items_endpoint += '?{params}'.format(params=urlencode(self.request.GET))
        conn = self.get_connection(conn_type="iam")
        group_choices = [] #sorted(set(conn.get_all_groups().groups))
        self.filter_fields = [
            LandingPageFilter(key='group', name='Groups', choices=group_choices),
        ]
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['user_name', 'user_id', 'arn', 'path']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='user_id', name='ID'),
            dict(key='name', name=_(u'User name')),
            dict(key='path', name=_(u'Path')),
        ]

        return dict(
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
        )


class UsersJsonView(BaseView):
    """Users returned as JSON"""
    @view_config(route_name='users_json', renderer='json', request_method='GET')
    def users_json(self):
    # TODO: take filters into account??
        users = []
        for user in self.get_items():
            users.append(dict(
                path=user.path,
                user_name=user.user_name,
                user_id=user.user_id,
                arn=user.arn,
            ))
        return dict(results=users)

    def get_items(self):
        conn = self.get_connection(conn_type="iam")
        try:
            return conn.get_all_users().users
        except BotoServerError as exc:
            return BaseView.handle_403_error(exc, request=self.request)

class UserView(BaseView):
    """Views for single User"""
    TEMPLATE = '../templates/users/user_view.pt'
    NEW_TEMPLATE = '../templates/users/user_new.pt'

    def __init__(self, request):
        super(UserView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        self.user = self.get_user()
        self.user_form = UserForm(self.request, user=self.user, conn=self.conn, formdata=self.request.params or None)
        self.prefix = '/users'
        self.change_password_form = ChangePasswordForm(self.request)
        self.delete_form = DeleteUserForm(self.request)
        self.render_dict = dict(
            user=self.user,
            prefix=self.prefix,
            user_form=self.user_form,
            change_password_form=self.change_password_form,
            delete_form=self.delete_form,
        )

    def get_user(self):
        user_param = self.request.matchdict.get('name')
        if user_param:
            user = self.conn.get_user(user_name=user_param)
            return user
        else:
            return None

    def generatePassword(self):
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'
        random.seed = (os.urandom(1024))
        return ''.join(random.choice(chars) for i in range(12))

    def addQuotaLimit(self, statements, param, action, condition):
        val = self.request.params.get(param, None)
        if val:
            statements.append({'Effect': 'Limit', 'Action': action,
                'Resource': '*', 'Condition':{'NumericLessThanEquals':{condition: val}}})

    @view_config(route_name='user_view', renderer=TEMPLATE)
    def user_view(self):
        if self.user is None:
            raise HTTPNotFound
        return self.render_dict
 
    @view_config(route_name='user_new', renderer=NEW_TEMPLATE)
    def user_view(self):
        return self.render_dict
 
    @view_config(route_name='user_access_keys_json', renderer='json', request_method='GET')
    def user_keys_json(self):
        """Return user access keys list"""
        keys = self.conn.get_all_access_keys(user_name=self.user.user_name)
        for k in keys.list_access_keys_result.access_key_metadata:
            k.title = k.access_key_id
        return dict(results=keys.list_access_keys_result.access_key_metadata)

    @view_config(route_name='user_groups_json', renderer='json', request_method='GET')
    def user_groups_json(self):
        """Return user groups list"""
        groups = self.conn.get_groups_for_user(user_name=self.user.user_name)
        for g in groups.groups:
            g.title = g.group_name
        return dict(results=groups.groups)

    @view_config(route_name='user_create', renderer=TEMPLATE, request_method='POST')
    def user_create(self):
        # can't use regular form validation here. We allow empty values and the validation
        # code does not, so we need to roll our own below.
        # get user list
        users_json = self.request.params.get('users')
        # get quota info
        # now get the rest
        random_password = self.request.params.get('random_password', 'n')
        access_keys = self.request.params.get('access_keys', 'n')
        allow_all = self.request.params.get('allow_all', 'n')
        path = self.request.params.get('path', '/')
        try:
            if users_json:
                users = json.loads(users_json)
                for name in users.items():
                    user = self.conn.create_user(name, path)
                    policy = {}
                    policy['Version'] = '2011-04-01'
                    statements = []
                    if random_password == 'y':
                        self.conn.create_login_profile(name, self.generatePassword())
                    if access_keys == 'y':
                        self.conn.create_access_key(name)
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
                        's3_bucket_size', 's3:????', 's3:quota-bucketsize')
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
                        import logging; logging.info("policy being set to = "+json.dumps(policy, indent=2))
                        self.conn.put_user_policy(name, "user-all-access-plus-quotas", json.dumps(policy))
            msg = _(u'Successfully created user(s).')
            location = self.request.route_url('user_view', name=user.user_name)
            return HTTPFound(location=location)
        except BotoServerError as err:
            msg = err.message
            queue = Notification.ERROR
            self.request.session.flash(msg, queue=queue)
            location = self.request.route_url('users')
            return HTTPFound(location=location)

 
    @view_config(route_name='user_update', request_method='POST', renderer='json')
    def user_update(self):
        """ calls iam:UpdateUser """
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
            return dict(message=err.message,
                        error=getattr(err, 'status', 400))

    @view_config(route_name='user_change_password', request_method='POST', renderer='json')
    def user_change_password(self):
        """ calls iam:UpdateLoginProfile """
        try:
            password = self.request.params.get('password')
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
            new_pass = self.request.params.get('new_password')
            try:
                # try to fetch login profile.
                self.conn.get_login_profiles(user_name=self.user.user_name)
                # if that worked, update the profile
                result = self.conn.update_login_profile(user_name=self.user.user_name, password=new_pass)
            except BotoServerError:
                # if that failed, create the profile
                result = self.conn.create_login_profile(user_name=self.user.user_name, password=new_pass)
            return dict(message=_(u"Successfully set user password"),
                        results="true")
        except BotoServerError as err:  # catch error in password change
            return dict(message=err.message,
                        error=getattr(err, 'status', 400))
        except HTTPError, err:          # catch error in authentication
            return dict(message=err.message,
                        error=getattr(err, 'status', 401))
        except URLError, err:           # catch error in authentication
            return dict(message=err.message,
                        error=getattr(err, 'status', 401))

    @view_config(route_name='user_generate_keys', request_method='POST', renderer='json')
    def user_genKeys(self):
        """ calls iam:CreateAccessKey """
        try:
            result = self.conn.create_access_key(user_name=self.user.user_name)
            self.user = self.get_user()
            return dict(message=_(u"Successfully generated keys"),
                        results=self.user)
        except BotoServerError as err:
            return dict(message=err.message,
                        error=getattr(err, 'status', 400))

    @view_config(route_name='user_add_to_group', request_method='POST', renderer='json')
    def user_add_to_group(self):
        """ calls iam:AddUserToGroup """
        try:
            group = self.request.params.get('group')
            result = self.conn.add_user_to_group(user_name=self.user.user_name, group=group)
            return dict(message=_(u"Successfully added user to group"),
                        results=result)
        except BotoServerError as err:
            return dict(message=err.message,
                        error=getattr(err, 'status', 400))

    @view_config(route_name='user_delete', request_method='POST')
    def user_delete(self):
        if self.user is None:
            raise HTTPNotFound
        try:
            self.conn.delete_user(user_name=self.user.user_name)
            location = self.request.route_url('users')
            msg = _(u'Successfully deleted user')
            queue = Notification.SUCCESS
        except BotoServerError as err:
            location = self.request.route_url('user', name=self.user.user_name)
            msg = err.message
            queue = Notification.ERROR
        self.request.session.flash(msg, queue=queue)
        return HTTPFound(location=location)
