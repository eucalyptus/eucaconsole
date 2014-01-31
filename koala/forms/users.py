# -*- coding: utf-8 -*-
"""
Forms for Users 

"""
import simplejson as json

import wtforms
from wtforms import validators
from wtforms import widgets

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class UserForm(BaseSecureForm):
    """User form
       Note: no need to add a 'users' field.  Use the user_editor panel (in a template) instead
       Only need to initialize as a secure form to generate CSRF token
    """
    # these fields used for new user form
    random_password = wtforms.BooleanField(label=_(u"Create and download random password"))
    access_keys = wtforms.BooleanField(label=_(u"Create and download access keys"))
    allow_all = wtforms.BooleanField(label=_(u"Allow read/write access to all resource except users and groups"))

    path = wtforms.TextField(label=_(u"Path"), default="/")

    ec2_images_max = wtforms.IntegerField(label=_(u'Images (maximum)'))
    ec2_instances_max = wtforms.IntegerField(label=_(u'Instances (maximum)'))
    ec2_volumes_max = wtforms.IntegerField(label=_(u'Volumes (maximum)'))
    ec2_total_size_all_vols = wtforms.IntegerField(label=_(u'Total size of all volumes (GB)'))
    ec2_snapshots_max = wtforms.IntegerField(label=_(u'Snapshots (maximum)'))
    ec2_elastic_ip_max = wtforms.IntegerField(label=_(u'Elastic IP addresses (maximum)'))

    s3_buckets_max = wtforms.IntegerField(label=_(u'Buckets (maximum)'))
    s3_objects_per_max = wtforms.IntegerField(label=_(u'Objects per bucket (maximum)'))
    s3_bucket_size = wtforms.IntegerField(label=_(u'Size of each bucket (MB)'))
    s3_total_size_all_buckets = wtforms.IntegerField(label=_(u'Total size of all buckets (maximum)'))

    autoscale_groups_max = wtforms.IntegerField(label=_(u'Auto scaling groups (maximum)'))
    launch_configs_max = wtforms.IntegerField(label=_(u'Launch configurations (maximum)'))
    scaling_policies_max = wtforms.IntegerField(label=_(u'Scaling policies (maximum)'))

    elb_load_balancers_max = wtforms.IntegerField(label=_(u'Load balancers (maximum)'))

    iam_groups_max = wtforms.IntegerField(label=_(u'Groups (maximum)'))
    iam_users_max = wtforms.IntegerField(label=_(u'Users (maximum)'))
    iam_roles_max = wtforms.IntegerField(label=_(u'Roles (maximum)'))
    iam_inst_profiles_max = wtforms.IntegerField(label=_(u'Instance profiles (maximum)'))

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
            policy_json = self.conn.get_user_policy(user_name=user.user_name,
                                policy_name="user-all-access-plus-quotas").policy_document
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
                                self.ec2_images_max.data = limit
                            elif val == 'ec2:quota-vminstancenumber':
                                self.ec2_instances_max.data = limit
                            elif val == 'ec2:quota-volumenumber':
                                self.ec2_volumes_max.data = limit
                            elif val == 'ec2:quota-snapshotnumber':
                                self.ec2_snapshots_max.data = limit
                            elif val == 'ec2:quota-volumetotalsize':
                                self.ec2_total_size_all_vols = limit
                            elif val == 'ec2:quota-addressnumber':
                                self.ec2_elastic_ip_max = limit
                            elif val == 's3:quota-bucketnumber':
                                self.s3_buckets_max = limit
                            elif val == 's3:quota-bucketobjectnumber':
                                self.s3_objects_per_max = limit
                            elif val == 's3:quota-bucketsize':
                                self.s3_bucket_size = limit
                            elif val == 's3:quota-buckettotalsize':
                                self.s3_total_size_all_buckets = limit
                            elif val == 'autoscaling:quota-autoscalinggroupnumber':
                                self.autoscale_groups_max = limit
                            elif val == 'autoscaling:quota-launchconfigurationnumber':
                                self.launch_configs_max = limit
                            elif val == 'autoscaling:quota-scalingpolicynumber':
                                self.scaling_policies_max = limit
                            elif val == 'elasticloadbalancing:quota-loadbalancernumber':
                                self.elb_load_balancers_max = limit
                            elif val == 'iam:quota-groupnumber':
                                self.iam_groups_max = limit
                            elif val == 'iam:quota-usernumber':
                                self.iam_users_max = limit
                            elif val == 'iam:quota-rolenumber':
                                self.iam_roles_max = limit
                            elif val == 'iam:quota-instanceprofilenumber':
                                self.iam_inst_profiles_max = limit
                                

class ChangePasswordForm(BaseSecureForm):
    """CSRF-protected form to delete a user"""
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

