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
Forms for Users 

"""
import simplejson as json

from boto.exception import BotoServerError

import wtforms
from wtforms import validators
from wtforms import widgets

from ..i18n import _
from . import BaseSecureForm, TextEscapedField


class UserForm(BaseSecureForm):
    """User form
       Note: no need to add a 'users' field.  Use the user_editor panel (in a template) instead
       Only need to initialize as a secure form to generate CSRF token
    """
    # these fields used for new user form
    random_password = wtforms.BooleanField(label=_(u"Create and download random password"))
    access_keys = wtforms.BooleanField(label=_(u"Create and download access keys"))
    allow_all = wtforms.BooleanField(label=_(u"Allow read/write access to all resource except users and groups"))

    path = TextEscapedField(label=_(u"Path"), default="/")

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

    # additional items used for update user form
    user_name = wtforms.TextField(label=_(u"Name"))
    email = wtforms.TextField(label=_(u"E-mail address"))
    new_password = wtforms.PasswordField(
        _(u'New password'),
        validators=[
            validators.InputRequired(message=_(u'New Password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())
    new_password2 = wtforms.PasswordField(
        _(u'Confirm new password'),
        validators=[
            validators.InputRequired(message=_(u'New Password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())

    download_keys = wtforms.BooleanField(label=_(u"Download keys after generation"))

    def __init__(self, request, user=None, conn=None, **kwargs):
        super(UserForm, self).__init__(request, **kwargs)
        self.user = user
        self.conn = conn
        if user is not None:
            self.user_name.data = user.user_name
            self.path.data = user.path
            try:
                policies = self.conn.get_all_user_policies(user_name=user.user_name)
                for policy_name in policies.policy_names:
                    policy_json = self.conn.get_user_policy(user_name=user.user_name,
                                        policy_name=policy_name).policy_document
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
                                        self.setLowest(self.ec2_images_max, limit)
                                    elif val == 'ec2:quota-vminstancenumber':
                                        self.setLowest(self.ec2_instances_max, limit)
                                    elif val == 'ec2:quota-volumenumber':
                                        self.setLowest(self.ec2_volumes_max, limit)
                                    elif val == 'ec2:quota-snapshotnumber':
                                        self.setLowest(self.ec2_snapshots_max, limit)
                                    elif val == 'ec2:quota-volumetotalsize':
                                        self.setLowest(self.ec2_total_size_all_vols, limit)
                                    elif val == 'ec2:quota-addressnumber':
                                        self.setLowest(self.ec2_elastic_ip_max, limit)
                                    elif val == 's3:quota-bucketnumber':
                                        self.setLowest(self.s3_buckets_max, limit)
                                    elif val == 's3:quota-bucketobjectnumber':
                                        self.setLowest(self.s3_objects_per_max, limit)
                                    elif val == 's3:quota-bucketsize':
                                        self.setLowest(self.s3_bucket_size, limit)
                                    elif val == 's3:quota-buckettotalsize':
                                        self.setLowest(self.s3_total_size_all_buckets, limit)
                                    elif val == 'autoscaling:quota-autoscalinggroupnumber':
                                        self.setLowest(self.autoscale_groups_max, limit)
                                    elif val == 'autoscaling:quota-launchconfigurationnumber':
                                        self.setLowest(self.launch_configs_max, limit)
                                    elif val == 'autoscaling:quota-scalingpolicynumber':
                                        self.setLowest(self.scaling_policies_max, limit)
                                    elif val == 'elasticloadbalancing:quota-loadbalancernumber':
                                        self.setLowest(self.elb_load_balancers_max, limit)
                                    elif val == 'iam:quota-groupnumber':
                                        self.setLowest(self.iam_groups_max, limit)
                                    elif val == 'iam:quota-usernumber':
                                        self.setLowest(self.iam_users_max, limit)
                                    elif val == 'iam:quota-rolenumber':
                                        self.setLowest(self.iam_roles_max, limit)
                                    elif val == 'iam:quota-instanceprofilenumber':
                                        self.setLowest(self.iam_inst_profiles_max, limit)
            except BotoServerError as err:
                pass

    def setLowest(self, item, val):
        """ This function sets the field data value if the new value is lower than the current one """
        if item.data is None or item.data > val:
            item.data = val

class DisableUserForm(BaseSecureForm):
    """CSRF-protected form to disable a user"""
    pass

class EnableUserForm(BaseSecureForm):
    """CSRF-protected form to enable a user"""
    random_password = wtforms.BooleanField(label=_(u"Create and download random password"))

class ChangePasswordForm(BaseSecureForm):
    """CSRF-protected form to change a password """
    password = wtforms.PasswordField(
        _(u'Your password'),
        validators=[
            validators.InputRequired(message=_(u'A password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())

class GeneratePasswordForm(BaseSecureForm):
    """CSRF-protected form to generate a random password"""
    password = wtforms.PasswordField(
        _(u'Your password'),
        validators=[
            validators.InputRequired(message=_(u'A password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())

class DeleteUserForm(BaseSecureForm):
    """CSRF-protected form to delete a user"""
    pass

class AddToGroupForm(BaseSecureForm):
    group_error_msg = _(u'Group is required')
    group_name = wtforms.SelectField(
        validators=[validators.InputRequired(message=group_error_msg)],
    )
    def __init__(self, request, groups=None, **kwargs):
        super(AddToGroupForm, self).__init__(request, **kwargs)
        if groups is not None:
            choices = [(group, group) for group in groups]
            self.group_name.choices = choices
        else:
            self.group_name.choices = [('', '')]

