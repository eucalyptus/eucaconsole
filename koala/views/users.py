# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Users

"""
import os, random, string
from urllib import urlencode
import simplejson as json

from boto.exception import EC2ResponseError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config


from ..forms.users import UserForm
from ..models import Notification
from ..models import LandingPageFilter
from ..views import BaseView, LandingPageView, TaggedItemView


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
            display_type=self.display_type,
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
        except EC2ResponseError as exc:
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
        self.render_dict = dict(
            user=self.user,
            user_form=self.user_form,
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
        email_users = self.request.params.get('email_users', 'n')
        allow_all = self.request.params.get('allow_all', 'n')
        path = self.request.params.get('path', '/')
        try:
            if users_json:
                users = json.loads(users_json)
                for name, email in users.items():
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
        except EC2ResponseError as err:
            msg = err.message
            queue = Notification.ERROR
            self.request.session.flash(msg, queue=queue)
            location = self.request.route_url('users')
            return HTTPFound(location=location)
 
    @view_config(route_name='user_update', request_method='POST', renderer=TEMPLATE)
    def user_update(self):
        if self.user_form.validate():
            # TODO: do stuff...

            location = self.request.route_url('user_view', name=self.user.user_name)
            msg = _(u'Successfully modified user')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='user_delete', request_method='POST')
    def user_delete(self):
        if self.user is None:
            raise HTTPNotFound
            self.conn.delete_user(user_name=self.user.user_name)

            location = self.request.route_url('users')
            msg = _(u'Successfully deleted user')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return self.render_dict
