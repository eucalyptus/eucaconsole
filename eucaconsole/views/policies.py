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
Pyramid views for IAM Policies (permissions)

"""
import simplejson as json

from pyramid.view import view_config

from ..constants import policies, permissions, AWS_REGIONS
from ..forms import ChoicesManager
from ..forms.policies import IAMPolicyWizardForm
from ..i18n import _
from ..views import BaseView, JSONResponse, TaggedItemView
from . import boto_error_handler


class IAMPolicyWizardView(BaseView):
    """Create IAM Policy wizard"""
    TEMPLATE = '../templates/policies/iam_policy_wizard.pt'

    def __init__(self, request):
        super(IAMPolicyWizardView, self).__init__(request)
        self.request = request
        self.ec2_conn = self.get_connection()
        self.iam_conn = self.get_connection(conn_type='iam')
        self.policy_json_endpoint = self.request.route_path('iam_policy_json')
        self.create_form = IAMPolicyWizardForm(request=self.request, formdata=self.request.params or None)
        self.target_type = self.request.params.get('type', 'user')  # 'account', 'user', 'group' or 'role'
        self.target_name = self.request.params.get('id', '')  # account, user, group or role name
        self.target_route = '{0}_view'.format(self.target_type)  # 'account_view', 'user_view', 'group_view' or 'role_view'
        self.location = self.request.route_path(self.target_route, name=self.target_name)
        with boto_error_handler(request):
            self.choices_manager = ChoicesManager(conn=self.ec2_conn)
            self.render_dict = dict(
                page_title=self.get_page_title(),
                create_form=self.create_form,
                cancel_link_url=self.location,
                policy_json_endpoint=self.policy_json_endpoint,
                policy_actions=permissions.POLICY_ACTIONS,
                controller_options=json.dumps(self.get_controller_options()),
                resource_choices=dict(
                    instances=self.get_instance_choices(),
                    images=self.get_image_choices(),
                    volumes=self.get_volume_choices(),
                    snapshots=self.get_snapshot_choices(),
                    security_groups=self.get_security_group_choices(),
                    key_pairs=self.get_key_pair_choices(),
                    vm_types=self.get_vm_type_choices(),
                    availability_zones=self.get_availability_zone_choices(),
                ),
            )

    @view_config(route_name='iam_policy_new', renderer=TEMPLATE, request_method='GET')
    def iam_policy_new(self):
        """Displays the Create IAM Policy wizard"""
        return self.render_dict

    @view_config(route_name='iam_policy_create', request_method='POST', renderer='json')
    def iam_policy_create(self):
        """Handles the POST from the Create IAM Policy wizard"""
        # redirect to detail page after submit
        if self.create_form.validate():
            policy_name = self.request.params.get('name')
            policy_json = self.request.params.get('policy', '{}')
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Creating policy {0} for {1} {2}").format(
                    policy_name, self.target_type, self.target_name))
                result = None
                if self.target_type == 'account':
                    result = self.iam_conn.get_response(
                                'PutAccountPolicy',
                                 params={'AccountName':self.target_name, 'PolicyName':policy_name,
                                         'PolicyDocument':policy_json},
                                 verb='POST'
                             )
                elif self.target_type == 'user':
                    caller = self.iam_conn.put_user_policy
                elif self.target_type == 'group':
                    caller = self.iam_conn.put_group_policy
                else:
                    caller = self.iam_conn.put_role_policy
                if not(result):
                    result = caller(self.target_name, policy_name, policy_json)
                return dict(message=_(u"Successfully updated user policy"), results=result)
        else:
            error_messages = self.create_form.get_errors_list()
            return JSONResponse(status=400, message=", ".join(error_messages))

    def get_page_title(self):
        prefix = _(u'Add access policy for')
        return '{0} {1} {2}'.format(prefix, self.target_type.capitalize(), self.target_name)

    def get_controller_options(self):
        return {
            'policyJsonEndpoint': self.policy_json_endpoint,
            'cloudType': self.cloud_type,
            'actionsList': self.get_all_actions(),
            'languageCode': self.get_language_code(),
            'awsRegions': AWS_REGIONS,
            'existingPolicies': json.dumps(self.get_existing_policies()),
        }

    def get_existing_policies(self):
        if self.target_type == 'account':
            iam_policies = self.iam_conn.get_response(
                                'ListAccountPolicies',
                                params={'AccountName':self.target_name},
                                list_marker='PolicyNames')
            return iam_policies.policy_names if iam_policies else []
        elif self.target_type == 'user':
            fetch_policies = self.iam_conn.get_all_user_policies
        elif self.target_type == 'group':
            fetch_policies = self.iam_conn.get_all_group_policies
        else:
            fetch_policies = self.iam_conn.list_role_policies
        iam_policies = fetch_policies(self.target_name)
        return iam_policies.policy_names if iam_policies else []

    def get_instance_choices(self):
        resource_name = 'instance'
        arn_prefix = self.get_arn_prefix(resource_name)
        choices = [(self.get_all_choice(resource_name), _(u'All instances...'))]
        for instance in self.ec2_conn.get_only_instances():
            value = '{0}{1}'.format(arn_prefix, instance.id)
            label = TaggedItemView.get_display_name(instance)
            choices.append((value, label))
        return choices

    def get_vm_type_choices(self):
        resource_name = 'vmtype'
        arn_prefix = self.get_arn_prefix(resource_name)
        choices = [(self.get_all_choice(resource_name), _(u'All instance types...'))]
        vm_type_choices = self.choices_manager.instance_types(
            cloud_type=self.cloud_type, add_blank=False, add_description=False)
        for vm_type_choice in vm_type_choices:
            label = vm_type_choice[1]
            value = '{0}{1}'.format(arn_prefix, vm_type_choice[0])
            choices.append((value, label))
        return choices

    def get_image_choices(self):
        resource_name = 'image'
        arn_prefix = self.get_arn_prefix(resource_name)
        choices = [(self.get_all_choice(resource_name), _(u'All images...'))]
        # Set owner alias to 'self' for AWS
        owner_alias = 'self' if self.cloud_type == 'aws' else None
        owners = [owner_alias] if owner_alias else []
        images = self.ec2_conn.get_all_images(owners=owners, filters={'image-type': 'machine'})
        for image in images:
            value = '{0}{1}'.format(arn_prefix, image.id)
            label = TaggedItemView.get_display_name(image)
            choices.append((value, label))
        return choices

    def get_volume_choices(self):
        resource_name = 'volume'
        arn_prefix = self.get_arn_prefix(resource_name)
        choices = [(self.get_all_choice(resource_name), _(u'All volumes...'))]
        for volume in self.ec2_conn.get_all_volumes():
            value = '{0}{1}'.format(arn_prefix, volume.id)
            label = TaggedItemView.get_display_name(volume)
            choices.append((value, label))
        return choices

    def get_snapshot_choices(self):
        resource_name = 'snapshot'
        arn_prefix = self.get_arn_prefix(resource_name)
        choices = [(self.get_all_choice(resource_name), _(u'All snapshots...'))]
        for snapshot in self.ec2_conn.get_all_snapshots(owner='self'):
            value = '{0}{1}'.format(arn_prefix, snapshot.id)
            label = TaggedItemView.get_display_name(snapshot)
            choices.append((value, label))
        return choices

    def get_security_group_choices(self):
        resource_name = 'securitygroup'
        arn_prefix = self.get_arn_prefix(resource_name)
        choices = [(self.get_all_choice(resource_name), _(u'All security groups...'))]
        for security_group in self.ec2_conn.get_all_security_groups():
            value = '{0}{1}'.format(arn_prefix, security_group.name)
            label = '{0} ({1})'.format(security_group.name, security_group.id)
            choices.append((value, label))
        return choices

    def get_availability_zone_choices(self):
        resource_name = 'availabilityzone'
        region = self.request.session.get('region')
        arn_prefix = self.get_arn_prefix(resource_name)
        choices = [(self.get_all_choice(resource_name), _(u'All zones...'))]
        for avail_zone_choice in self.choices_manager.availability_zones(region, add_blank=False):
            value = '{0}{1}'.format(arn_prefix, avail_zone_choice[0])
            label = avail_zone_choice[0]
            choices.append((value, label))
        return choices

    def get_key_pair_choices(self):
        resource_name = 'keypair'
        arn_prefix = self.get_arn_prefix(resource_name)
        choices = [(self.get_all_choice(resource_name), _(u'All key pairs...'))]
        for key_pair in self.ec2_conn.get_all_key_pairs():
            value = '{0}{1}'.format(arn_prefix, key_pair.name)
            label = key_pair.name
            choices.append((value, label))
        return choices

    def get_arn_prefix(self, resource, add_all=False):
        region = ''
        if self.cloud_type == 'aws':
            region = self.region
        return 'arn:aws:ec2:{region}::{resource}/{all}'.format(
            region=region, resource=resource, all='*' if add_all else '')

    def get_all_choice(self, resource):
        return self.get_arn_prefix(resource, add_all=True)

    def get_language_code(self):
        if self.request.accept_language and self.request.accept_language.header_value:
            return self.request.accept_language.header_value[:2]
        return 'en'

    @staticmethod
    def get_all_actions():
        actions = []
        for namespace in permissions.POLICY_ACTIONS:
            actions.extend(namespace.get('actions'))
        return actions


class IAMPolicyWizardJsonView(BaseView):
    """View for returning JSON of canned policies"""

    @view_config(route_name='iam_policy_json', renderer='json', request_method='GET')
    def iam_policy_json(self):
        policy_type = self.request.params.get('type')
        policy_dict = policies.TYPE_POLICY_MAPPING.get(policy_type)
        if policy_dict:
            return dict(policy=policy_dict)
        return JSONResponse(status=404, message=_(u'Unable to locate policy'))
