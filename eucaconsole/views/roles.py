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
Pyramid views for Eucalyptus and AWS Roles

"""
from datetime import datetime
from dateutil import parser
import simplejson as json
from urllib import urlencode

from boto.exception import BotoServerError
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.roles import RoleForm, DeleteRoleForm
from ..models import Notification
from ..views import BaseView, LandingPageView, JSONResponse, TaggedItemView
from . import boto_error_handler


class RolesView(LandingPageView):
    TEMPLATE = '../templates/roles/roles.pt'

    def __init__(self, request):
        super(RolesView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        self.initial_sort_key = 'role_name'
        self.prefix = '/roles'
        self.delete_form = DeleteRoleForm(self.request, formdata=self.request.params or None)

    @view_config(route_name='roles', renderer=TEMPLATE)
    def roles_landing(self):
        json_items_endpoint = self.request.route_path('roles_json')
        if self.request.GET:
            json_items_endpoint += '?{params}'.format(params=urlencode(self.request.GET))
        user_choices = []  # sorted(set(item.user_name for item in conn.get_all_users().users))
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['path', 'role_name', 'role_id', 'arn']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='role_name', name=_(u'Role name: A to Z')),
            dict(key='-role_name', name=_(u'Role name: Z to A')),
        ]

        return dict(
            filter_fields=False,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
            delete_form=self.delete_form,
        )

    @view_config(route_name='roles_delete', request_method='POST')
    def roles_delete(self):
        location = self.request.route_path('roles')
        role_name = self.request.params.get('name')
        role = self.conn.get_role(role_name=role_name)
        if role and self.delete_form.validate():
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Deleting role {0}").format(role.role_name))
                params = {'RoleName': role.role_name, 'IsRecursive': 'true'}
                self.conn.get_response('DeleteRole', params)
                msg = _(u'Successfully deleted role')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            msg = _(u'Unable to delete role.')  # TODO Pull in form validation error messages here
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=location)


class RolesJsonView(BaseView):
    """Roles returned as JSON"""
    def __init__(self, request):
        super(RolesJsonView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")

    @view_config(route_name='roles_json', renderer='json', request_method='GET')
    def roles_json(self):
        # TODO: take filters into account??
        roles = []
        for role in self.get_items():
            policies = []
            try:
                policies = self.conn.list_role_policies(role_name=role.role_name)
                policies = policies.policy_names
            except BotoServerError as exc:
                pass
            """
            user_count = 0
            try:
                role = self.conn.get_role(role_name=role.role_name)
                user_count = len(role.users) if hasattr(role, 'users') else 0
            except BotoServerError as exc:
                pass
            """
            roles.append(dict(
                path=role.path,
                role_name=role.role_name,
                create_date=role.create_date,
                policy_count=len(policies),
            ))
        return dict(results=roles)

    def get_items(self):
        with boto_error_handler(self.request):
            return self.conn.list_roles().roles


class RoleView(BaseView):
    """Views for single Role"""
    TEMPLATE = '../templates/roles/role_view.pt'

    def __init__(self, request):
        super(RoleView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        self.role = self.get_role()
        self.role_route_id = self.request.matchdict.get('name')
        self.all_users = self.get_all_users_array()
        self.role_form = RoleForm(self.request, role=self.role, formdata=self.request.params or None)
        self.delete_form = DeleteRoleForm(self.request, formdata=self.request.params)
        create_date = parser.parse(self.role.create_date) if self.role else datetime.now()
        self.render_dict = dict(
            role=self.role,
            role_create_date=create_date,
            role_route_id=self.role_route_id,
            all_users=self.all_users,
            role_form=self.role_form,
            delete_form=self.delete_form,
        )

    def get_role(self):
        role_param = self.request.matchdict.get('name')
        # Return None if the request is to create new role. Prob. No rolename "new" can be created
        if role_param == "new" or role_param is None:
            return None
        role = None
        try:
            role = self.conn.get_role(role_name=role_param)
            role = role.get_role_response.get_role_result.role
        except BotoServerError as err:
            pass
        return role

    def get_all_users_array(self):
        role_param = self.request.matchdict.get('name')
        if role_param == "new" or role_param is None:
            return []
        users = []
        # Role's path to be used ?
        if self.conn:
            users = [u.user_name.encode('ascii', 'ignore') for u in self.conn.get_all_users().users]
        return users

    def _get_trusted_entity_(self, parsed_policy):
        principal = parsed_policy['Statement'][0]['Principal']
        if 'AWS' in principal.keys():
            arn = principal['AWS']
            return _(u'Accout ') + arn[arn.rindex('::')+2:arn.rindex(':')]
        elif 'Service' in principal.keys():
            svc = principal['Service']
            if isinstance(svc, list):
                svc = svc[0]
            return _(u'Service ') + svc
        return ''

    @view_config(route_name='role_view', renderer=TEMPLATE)
    def role_view(self):
        self.render_dict['trusted_entity'] = ''
        self.render_dict['assume_role_policy_document'] = ''
        if self.role is not None:
            # first, prettify the trust doc
            parsed = json.loads(self.role.assume_role_policy_document)
            self.role.assume_role_policy_document=json.dumps(parsed, indent=2)
            # and pull out the trusted acct id
            self.render_dict['trusted_entity'] = self._get_trusted_entity_(parsed)
            self.render_dict['assume_role_policy_document'] = self.role.assume_role_policy_document
            with boto_error_handler(self.request):
                instances = []
                profiles = self.conn.list_instance_profiles()
                profiles = profiles.list_instance_profiles_response.list_instance_profiles_result.instance_profiles
                profile_arns = [profile.arn for profile in profiles if profile.roles.member.role_name == self.role.role_name]
                results = self.get_connection().get_only_instances()
                for instance in results:
                    if len(instance.instance_profile) > 0 and instance.instance_profile['arn'] in profile_arns:
                        instance.name=TaggedItemView.get_display_name(instance)
                        instances.append(instance)
                # once https://eucalyptus.atlassian.net/browse/EUCA-9692 is fixed, use line below instead
                #instances = self.get_connection().get_only_instances(filters={'iam-instance-profile.arn':profile_arns})
                self.render_dict['instances'] = instances
        return self.render_dict
 
    @view_config(route_name='role_create', request_method='POST', renderer=TEMPLATE)
    def role_create(self):
        if self.role_form.validate():
            new_role_name = self.request.params.get('role_name') 
            role_type = self.request.params.get('roletype')
            if role_type == 'xacct':
                acct_id = self.request.params.get('accountid')
                external_id = self.request.params.get('externalid')
            new_path = self.request.params.get('path')
            err_location = self.request.route_path('roles')
            with boto_error_handler(self.request, err_location):
                self.log_request(_(u"Creating role {0}").format(new_role_name))
                if role_type == 'xacct':
                    policy = {'Version': '2012-10-17'}
                    statement = {'Effect': 'Allow', 'Action': 'sts:AssumeRole'}
                    statement['Principal'] = {'AWS': "arn:aws:iam::%s:root" % (acct_id)}
                    if len(external_id) > 0:
                        statement['Condition'] = {'StringEquals': {'sts:ExternalId': external_id}}
                    policy['Statement'] = [statement]
                    self.conn.create_role(role_name=new_role_name, path=new_path, assume_role_policy_document=json.dumps(policy))
                else:
                    self.conn.create_role(role_name=new_role_name, path=new_path)
                msg_template = _(u'Successfully created role {role}')
                msg = msg_template.format(role=new_role_name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            location = self.request.route_path('iam_policy_new') + '?type=role&id=' + new_role_name
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='role_delete', request_method='POST')
    def role_delete(self):
        if not self.delete_form.validate():
            return JSONResponse(status=400, message="missing CSRF token")
        location = self.request.route_path('roles')
        if self.role is None:
            raise HTTPNotFound()
        with boto_error_handler(self.request, location):
            self.log_request(_(u"Deleting role {0}").format(self.role.role_name))
            params = {'RoleName': self.role.role_name, 'IsRecursive': 'true'}
            self.conn.get_response('DeleteRole', params)
            msg = _(u'Successfully deleted role')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
        return HTTPFound(location=location)

    @view_config(route_name='role_policies_json', renderer='json', request_method='GET')
    def role_policies_json(self):
        " ""Return role policies list" ""
        with boto_error_handler(self.request):
            policies = self.conn.list_role_policies(role_name=self.role.role_name)
            return dict(results=policies.policy_names)

    @view_config(route_name='role_policy_json', renderer='json', request_method='GET')
    def role_policy_json(self):
        " ""Return role policies list" ""
        with boto_error_handler(self.request):
            policy_name = self.request.matchdict.get('policy')
            policy = self.conn.get_role_policy(role_name=self.role.role_name, policy_name=policy_name)
            parsed = json.loads(policy.policy_document)
            return dict(results=json.dumps(parsed, indent=2))

    @view_config(route_name='role_update_policy', request_method='POST', renderer='json')
    def role_update_policy(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        # calls iam:PutRolePolicy
        policy = self.request.matchdict.get('policy')
        with boto_error_handler(self.request):
            self.log_request(_(u"Updating policy {0} for role {1}").format(policy, self.role.role_name))
            policy_text = self.request.params.get('policy_text')
            result = self.conn.put_role_policy(
                role_name=self.role.role_name, policy_name=policy, policy_document=policy_text)
            return dict(message=_(u"Successfully updated role policy"), results=result)

    @view_config(route_name='role_update_trustpolicy', request_method='POST', renderer='json')
    def role_update_trustpolicy(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        # calls iam:UpdateAssumeRolePolicy
        with boto_error_handler(self.request):
            self.log_request(_(u"Updating trust policy for role {0}").format(self.role.role_name))
            policy_text = self.request.params.get('policy_text')
            result = self.conn.update_assume_role_policy(
                role_name=self.role.role_name, policy_document=policy_text)
            parsed = json.loads(policy_text)
            return dict(message=_(u"Successfully updated trust role policy"), results=result, trusted_entity=self._get_trusted_entity_(parsed))

    @view_config(route_name='role_delete_policy', request_method='POST', renderer='json')
    def role_delete_policy(self):
        if not self.is_csrf_valid():
            return JSONResponse(status=400, message="missing CSRF token")
        # calls iam:DeleteRolePolicy
        policy = self.request.matchdict.get('policy')
        with boto_error_handler(self.request):
            self.log_request(_(u"Deleting policy {0} for role {1}").format(policy, self.role.role_name))
            result = self.conn.delete_role_policy(role_name=self.role.role_name, policy_name=policy)
            return dict(message=_(u"Successfully deleted role policy"), results=result)

