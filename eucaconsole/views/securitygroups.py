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
Pyramid views for Eucalyptus and AWS security groups

"""
import simplejson as json
import socket

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from ..forms.securitygroups import SecurityGroupForm, SecurityGroupDeleteForm, SecurityGroupsFiltersForm
from ..i18n import _
from ..models import Notification
from ..views import BaseView, LandingPageView, TaggedItemView, JSONResponse
from . import boto_error_handler
from ..constants.internet_protocols import INTERNET_PROTOCOL_NUMBERS


class SecurityGroupsView(LandingPageView):
    TEMPLATE = '../templates/securitygroups/securitygroups.pt'

    def __init__(self, request):
        super(SecurityGroupsView, self).__init__(request)
        self.conn = self.get_connection()
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.initial_sort_key = 'name'
        self.prefix = '/securitygroups'
        self.json_items_endpoint = self.get_json_endpoint('securitygroups_json')
        self.delete_form = SecurityGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.filters_form = SecurityGroupsFiltersForm(
            self.request, vpc_conn=self.vpc_conn, cloud_type=self.cloud_type,
            formdata=self.request.params or None)
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        if not self.is_vpc_supported:
            del self.filters_form.vpc_id
        self.render_dict = dict(
            prefix=self.prefix,
            delete_form=self.delete_form,
            filters_form=self.filters_form,
            is_vpc_supported=self.is_vpc_supported,
        )

    @view_config(route_name='securitygroups', renderer=TEMPLATE)
    def securitygroups_landing(self):
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['name', 'description', 'vpc_id', 'tags']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='description', name=_(u'Description')),
        ]
        self.render_dict.update(dict(
            filter_fields=True,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
        ))
        return self.render_dict

    @view_config(route_name='securitygroups_delete', request_method='POST')
    def securitygroups_delete(self):
        securitygroup_id = self.request.params.get('securitygroup_id')
        security_group = self.get_security_group(securitygroup_id)
        location = self.get_redirect_location('securitygroups')
        if security_group and self.delete_form.validate():
            name = security_group.name
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Deleting security group {0}").format(name))
                security_group.delete()
                prefix = _(u'Successfully deleted security group')
                msg = '{0} {1}'.format(prefix, name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            msg = _(u'Unable to delete security group')
            self.request.session.flash(msg, queue=Notification.ERROR)
            return HTTPFound(location=location)

    def get_security_group(self, group_id=None):
        group_param = group_id
        if group_param is None:
            return None  # If missing, we're going to return an empty security group form
        groupids = [group_param]
        security_groups = self.conn.get_all_security_groups(group_ids=groupids)
        security_group = security_groups[0] if security_groups else None
        return security_group

    @staticmethod
    def get_rules(rules, rule_type='inbound'):
        rules_list = []
        for rule in rules:
            grants = [
                dict(name=g.name, owner_id=g.owner_id, group_id=g.group_id, cidr_ip=g.cidr_ip) for g in rule.grants
            ]
            rules_list.append(dict(
                ip_protocol=rule.ip_protocol,
                from_port=rule.from_port,
                to_port=rule.to_port,
                grants=grants,
                rule_type=rule_type,
            ))
        return rules_list


class SecurityGroupsJsonView(LandingPageView):
    def __init__(self, request):
        super(SecurityGroupsJsonView, self).__init__(request)
        self.conn = self.get_connection()
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.vpcs = self.get_all_vpcs()

    @view_config(route_name='securitygroups_json', renderer='json', request_method='POST')
    def securitygroups_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        securitygroups = []
        vpc_id = self.request.params.get('vpc_id')
        for securitygroup in self.filter_items(self.get_items()):
            if vpc_id != '' or (vpc_id == '' and securitygroup.vpc_id is None):
                vpc_name = ''
                if securitygroup.vpc_id != '':
                    vpc = self.get_vpc_by_id(securitygroup.vpc_id)
                    vpc_name = TaggedItemView.get_display_name(vpc) if vpc else ''
                securitygroups.append(dict(
                    id=securitygroup.id,
                    description=securitygroup.description,
                    name=securitygroup.name,
                    owner_id=securitygroup.owner_id,
                    vpc_id=securitygroup.vpc_id,
                    vpc_name=vpc_name,
                    rules=SecurityGroupsView.get_rules(securitygroup.rules),
                    rules_egress=SecurityGroupsView.get_rules(securitygroup.rules_egress, rule_type='outbound'),
                    tags=TaggedItemView.get_tags_display(securitygroup.tags),
                ))
        return dict(results=securitygroups)

    @view_config(route_name='securitygroups_rules_json', renderer='json', request_method='POST')
    def get_securitygroups_rules(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        securitygroups = []
        if self.conn:
            securitygroups = self.conn.get_all_security_groups()
        rules_dict = {}
        for security_group in securitygroups:
            rules = SecurityGroupsView.get_rules(security_group.rules)
            if security_group.vpc_id is not None:
                rules_egress = SecurityGroupsView.get_rules(security_group.rules_egress, rule_type='outbound')
                rules = rules + rules_egress 
            rules_dict[security_group.id] = rules
        return dict(results=rules_dict)

    def get_items(self):
        return self.conn.get_all_security_groups() if self.conn else []

    def get_all_vpcs(self):
        return self.vpc_conn.get_all_vpcs() if self.vpc_conn else []

    def get_vpc_by_id(self, vpc_id):
        for vpc in self.vpcs:
            if vpc_id == vpc.id:
                return vpc
        return None

    @view_config(route_name='internet_protocols_json', renderer='json', request_method='POST')
    def internet_protocols_json(self):
        internet_protocols = json.dumps({ 
            'internet_protocols': INTERNET_PROTOCOL_NUMBERS,
        })
        return dict(results=internet_protocols)


class SecurityGroupView(TaggedItemView):
    """Views for single Security Group"""
    TEMPLATE = '../templates/securitygroups/securitygroup_view.pt'

    def __init__(self, request):
        super(SecurityGroupView, self).__init__(request)
        self.conn = self.get_connection()
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.security_group = self.get_security_group()
        self.security_group_vpc = ''
        if self.security_group and self.security_group.vpc_id:
            self.vpc = self.vpc_conn.get_all_vpcs(vpc_ids=self.security_group.vpc_id)[0]
            self.security_group_vpc = TaggedItemView.get_display_name(self.vpc) if self.vpc else ''
        self.securitygroup_form = SecurityGroupForm(
            self.request, self.vpc_conn, security_group=self.security_group, formdata=self.request.params or None)
        self.delete_form = SecurityGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.security_group
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        controller_options_json = BaseView.escape_json(json.dumps({
            'default_vpc_network': self.get_default_vpc_network(),
        }))
        if not self.is_vpc_supported:
            del self.securitygroup_form.securitygroup_vpc_network
        self.render_dict = dict(
            security_group=self.security_group,
            security_group_name=self.escape_braces(self.security_group.name) if self.security_group else '',
            security_group_vpc=self.security_group_vpc,
            securitygroup_form=self.securitygroup_form,
            delete_form=self.delete_form,
            security_group_names=self.get_security_group_names(),
            controller_options_json=controller_options_json,
            is_vpc_supported=self.is_vpc_supported,
        )

    def get_default_vpc_network(self):
        default_vpc = self.request.session.get('default_vpc')
        if self.is_vpc_supported:
            if 'none' in default_vpc:
                if self.cloud_type == 'aws':
                    return 'None'
                # for euca, return the first vpc on the list
                if self.vpc_conn:
                    with boto_error_handler(self.request, self.location):
                        vpc_networks = self.vpc_conn.get_all_vpcs()
                        if vpc_networks:
                            return vpc_networks[0].id
            else:
                return default_vpc[0]
        return 'None'

    @view_config(route_name='securitygroup_view', renderer=TEMPLATE)
    def securitygroup_view(self):
        return self.render_dict

    @view_config(route_name='securitygroup_delete', renderer=TEMPLATE, request_method='POST')
    def securitygroup_delete(self):
        location = self.request.route_path('securitygroups')
        if self.security_group and self.delete_form.validate():
            name = self.security_group.name
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Deleting security group {0}").format(name))
                self.security_group.delete()
                prefix = _(u'Successfully deleted security group')
                msg = '{0} {1}'.format(prefix, name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='securitygroup_create', request_method='POST', renderer=TEMPLATE)
    def securitygroup_create(self):
        if self.securitygroup_form.validate():
            name = self.request.params.get('name')
            description = self.request.params.get('description')
            vpc_network = self.request.params.get('securitygroup_vpc_network') or None
            if vpc_network == 'None':
                vpc_network = None
            tags_json = self.request.params.get('tags')
            with boto_error_handler(self.request, self.request.route_path('securitygroups')):
                self.log_request(_(u"Creating security group {0}").format(name))
                temp_new_security_group = self.conn.create_security_group(name, description, vpc_id=vpc_network)
                # Need to retrieve security group to obtain complete VPC data
                new_security_group = self.get_security_group(temp_new_security_group.id)
                self.add_rules(security_group=new_security_group)
                if vpc_network is not None:
                    self.revoke_all_rules(security_group=new_security_group, traffic_type='egress')
                    self.add_rules(security_group=new_security_group, traffic_type='egress')
                if tags_json:
                    tags = json.loads(tags_json)
                    for tagname, tagvalue in tags.items():
                        new_security_group.add_tag(tagname, tagvalue)
                prefix = _(u'Successfully created security group')
                msg = '{0} {1}'.format(prefix, name)
                location = self.request.route_path('securitygroup_view', id=new_security_group.id)
                if self.request.is_xhr:
                    return JSONResponse(status=200, message=msg, id=new_security_group.id)
                else:
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                    return HTTPFound(location=location)
        if self.request.is_xhr:
            form_errors = ', '.join(self.securitygroup_form.get_errors_list())
            return JSONResponse(status=400, message=form_errors)  # Validation failure = bad request
        else:
            self.request.error_messages = self.securitygroup_form.get_errors_list()
            return self.render_dict

    @view_config(route_name='securitygroup_update', request_method='POST', renderer=TEMPLATE)
    def securitygroup_update(self):
        if self.request.params.get('securitygroup_vpc_network') is None: 
            del self.securitygroup_form.securitygroup_vpc_network
        if self.securitygroup_form.validate():
            # Update tags and rules
            location = self.request.route_path('securitygroup_view', id=self.security_group.id)
            with boto_error_handler(self.request, location=location):
                self.log_request(_(u"Replacing security group {0} tags").format(self.security_group.name))
                self.update_tags()
                self.log_request(_(u"Replacing security group {0} rules").format(self.security_group.name))
                self.update_rules()
            msg = _(u'Successfully modified security group')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.securitygroup_form.get_errors_list()
        return self.render_dict

    def get_security_group(self, group_id=None):
        group_param = group_id or self.request.matchdict.get('id')
        if group_param is None or group_param == 'new':
            return None  # If missing, we're going to return an empty security group form
        if group_param.startswith('sg-'):
            security_groups = self.conn.get_all_security_groups(filters={'group-id': [group_param]})
            security_group = security_groups[0] if security_groups else None
        else:  # Try name lookup
            security_groups = self.conn.get_all_security_groups(filters={'group-name': [group_param]})
            security_group = security_groups[0] if security_groups else None
        if security_group is None and group_param != 'new':
            raise HTTPNotFound()
        return security_group

    def exists_security_group(self, group_id=None):
        group_param = group_id
        if group_param is None:
            return None  # If missing, we're going to return an empty security group form
        groupids = [group_param]
        security_groups = self.conn.get_all_security_groups(group_ids=groupids)
        security_group = security_groups[0] if security_groups else None
        return security_group

    def get_security_group_names(self):
        groups = []
        if self.conn:
            if self.security_group:
                groups = [g.name for g in self.conn.get_all_security_groups() if self.security_group.vpc_id == g.vpc_id]
            else:
                groups = [g.name for g in self.conn.get_all_security_groups()]
        return sorted(set(groups))

    def add_rules(self, security_group=None, traffic_type='ingress'):
        if security_group is None:
            security_group = self.security_group
        # Now add the fresh set of rules
        if traffic_type == 'ingress':
            rules_json = self.request.params.get('rules')
        else:
            rules_json = self.request.params.get('rules_egress')
        rules = json.loads(rules_json) if rules_json else []

        for rule in rules:
            ip_protocol = self.get_protocol_by_name(rule.get('ip_protocol'))
            from_port = rule.get('from_port')
            to_port = rule.get('to_port')
            cidr_ip = None
            group_id = None
            group_name = None
            owner_id = None

            if from_port is not None and to_port is not None:
                from_port = int(from_port)
                to_port = int(to_port)
                if to_port < from_port:
                    to_port = from_port

            grants = rule.get('grants', [])

            for grant in grants:
                cidr_ip = grant.get('cidr_ip')
                group_name = grant.get('name')
                owner_id = grant.get('owner_id')
                group_id = grant.get('group_id')

            auth_args = dict(group_id=security_group.id, ip_protocol=ip_protocol,
                             from_port=from_port, to_port=to_port, cidr_ip=cidr_ip)

            if traffic_type == 'ingress':
                if group_id:
                    auth_args['src_security_group_group_id'] = group_id
                elif group_name:
                    auth_args['src_security_group_name'] = group_name
                if owner_id:
                    auth_args['src_security_group_owner_id'] = owner_id
            else:
                if group_id:
                    auth_args['src_group_id'] = group_id

            # If group_id is empty, or if group_id is not empty, make sure it hasn't been deleted
            if not group_id or self.exists_security_group(group_id) is not None:
                if traffic_type == 'ingress':
                    self.conn.authorize_security_group(**auth_args)
                else:
                    self.conn.authorize_security_group_egress(**auth_args)

    # Update security group rules when the request arrives
    def update_rules(self):
        self.update_ingress_rules()
        self.update_egress_rules()

    # Handle the update of the ingress rules
    def update_ingress_rules(self):
        # build rules dict for existing ingress rules
        current_rules = self.build_rules_dict(self.security_group.rules)
        # build rules dict for new ingress rules from the request
        new_rules_params = self.request.params.get('rules')
        new_rules = json.loads(new_rules_params) if new_rules_params else []
        # compare the rules and update the rules
        self.compare_and_update_rules(current_rules, new_rules)

    # Handle the update of the egress rules
    def update_egress_rules(self):
        # build rules dict for existing egress rules
        current_egress_rules = self.build_rules_dict(self.security_group.rules_egress, traffic_type='egress')
        # build rules dict for new egress rules from the request
        new_egress_rules_params = self.request.params.get('rules_egress')
        new_egress_rules = json.loads(new_egress_rules_params) if new_egress_rules_params else []
        # compare the rules and update the rules
        self.compare_and_update_rules(current_egress_rules, new_egress_rules, traffic_type='egress')

    @staticmethod
    def build_rules_dict(rules, traffic_type='ingress'):
        """Build security group rules dictionary for comparison and update purpose"""
        current_rules = []
        for rule in rules:
            grants = rule.grants
            from_port = int(rule.from_port) if rule.from_port else None
            to_port = int(rule.to_port) if rule.to_port else None
            params = dict(
                ip_protocol=rule.ip_protocol,
                from_port=from_port,
                to_port=to_port,
            )
            grants_params = []
            for grant in grants:
                g_params = {}
                if grant.cidr_ip:
                    g_params.update(dict(
                        cidr_ip=grant.cidr_ip,
                    ))
                elif grant.group_id:
                    if traffic_type == 'ingress':
                        g_params.update(dict(
                            src_security_group_group_id=grant.group_id,
                            src_security_group_owner_id=grant.owner_id,
                        ))
                    else:
                        g_params.update(dict(
                            src_group_id=grant.group_id,
                        ))
                grants_params.append(g_params)
            params.update(dict(grants=grants_params))
            # append the parameters into the rules dictionary
            current_rules.append(params)
        return current_rules

    def compare_and_update_rules(self, current_rules, new_rules, traffic_type='ingress'):
        """Compare the security group rules dictionaries and update added or removed rules"""
        self.compare_and_update_removed_rules(current_rules, new_rules, traffic_type)
        self.compare_and_update_added_rules(current_rules, new_rules, traffic_type)

    def compare_and_update_removed_rules(self, current_rules, new_rules, traffic_type='ingress'):
        """Detect the removed rules and make API calls to remove them"""
        # detect removed rules
        removed_rules_dict = self.detect_removed_rules(current_rules, new_rules, traffic_type)
        # convert the removed rules dict to boto params
        removed_rules = self.build_rules_params(removed_rules_dict, traffic_type)
        for rule in removed_rules:
            if traffic_type == 'ingress':
                self.conn.revoke_security_group(**rule)
            else:
                self.conn.revoke_security_group_egress(**rule)

    def compare_and_update_added_rules(self, current_rules, new_rules, traffic_type='ingress'):
        """Detect the added rules and make API calls to add them"""
        # detect added rules
        added_rules_dict = self.detect_added_rules(current_rules, new_rules, traffic_type)
        # convert the added rules dict to boto params
        added_rules = self.build_rules_params(added_rules_dict, traffic_type)
        for rule in added_rules:
            if traffic_type == 'ingress':
                self.conn.authorize_security_group(**rule)
            else:
                self.conn.authorize_security_group_egress(**rule)

    def build_rules_params(self, rules_dict, traffic_type='ingress'):
        """Build security group rules params from security group dictionary for boto calls"""
        rules_params = []
        for rule in rules_dict:
            ip_protocol = self.get_protocol_by_name(rule['ip_protocol'])
            from_port = rule['from_port']
            to_port = rule['to_port']
            grants = rule['grants']
            cidr_ip = None
            group_id = ''
            group_name = ''
            owner_id = ''
            # ensure that the from_port is greater than to_port
            if from_port is not None and to_port is not None:
                from_port = int(from_port)
                to_port = int(to_port)
                if to_port < from_port:
                    to_port = from_port
            # check each grant access for the rule
            for grant in grants:
                cidr_ip = grant['cidr_ip'] if 'cidr_ip' in grant else ''
                # detect the name of the source security group
                if 'name' in grant:
                    group_name = grant['name']
                elif 'src_security_group_name' in grant:
                    group_name = grant['src_security_group_name']
                # detect the owner id of the source security group
                if 'owner_id' in grant:
                    owner_id = grant['owner_id']
                elif 'src_security_group_owner_id' in grant:
                    owner_id = grant['src_security_group_owner_id']
                # detec the group id of the source security group
                if 'group_id' in grant:
                    group_id = grant['group_id']
                elif 'src_security_group_group_id' in grant:
                    group_id = grant['src_security_group_group_id']
                elif 'src_group_id' in grant:
                    group_id = grant['src_group_id']
            # create the argument dictionary for boto call
            auth_args = dict(group_id=self.security_group.id, ip_protocol=ip_protocol,
                             from_port=from_port, to_port=to_port, cidr_ip=cidr_ip)
            # the parameters below are different for EC2-Classic and EC2-VPC
            if traffic_type == 'ingress':
                if group_id:
                    auth_args['src_security_group_group_id'] = group_id
                elif group_name:
                    auth_args['src_security_group_name'] = group_name
                if owner_id:
                    auth_args['src_security_group_owner_id'] = owner_id
            else:
                if group_id:
                    auth_args['src_group_id'] = group_id
            # append the rules parameters
            rules_params.append(auth_args)
        return rules_params

    @staticmethod
    def detect_removed_rules(current_rules, new_rules, traffic_type='ingress'):
        """Detect removed rules and return the removed rules dictionary"""
        removed_rules = []
        # loop through current rules
        for rule in current_rules:
            is_removed = True
            c_grants = rule['grants']
            c_ip_protocol = rule['ip_protocol'] if rule['ip_protocol'] else None
            c_from_port = int(rule['from_port']) if rule['from_port'] else None
            c_to_port = int(rule['to_port']) if rule['to_port'] else None
            # loop through new rules
            for new_rule in new_rules:
                n_grants = new_rule['grants']
                n_ip_protocol = new_rule['ip_protocol'] if new_rule['ip_protocol'] else None
                n_from_port = int(new_rule['from_port']) if new_rule['from_port'] else None
                n_to_port = int(new_rule['to_port']) if new_rule['to_port'] else None
                # check if the ip protocol, from_port, and to_port match
                if c_ip_protocol == n_ip_protocol and c_from_port == n_from_port and c_to_port == n_to_port:
                    # check if the cidr_ip matches
                    if 'cidr_ip' in c_grants[0] and 'cidr_ip' in n_grants[0]:
                        if c_grants[0]['cidr_ip'] == n_grants[0]['cidr_ip']:
                            is_removed = False
                    elif traffic_type == 'ingress':
                        # check if source group id matches
                        if 'src_security_group_group_id' in c_grants[0] and 'group_id' in n_grants[0]:
                            if c_grants[0]['src_security_group_group_id'] == n_grants[0]['group_id']:
                                is_removed = False
                    elif traffic_type == 'egress':
                        # check if source group id matches
                        if 'src_group_id' in c_grants[0] and 'group_id' in n_grants[0]:
                            if c_grants[0]['src_group_id'] == n_grants[0]['group_id']:
                                is_removed = False
            if is_removed:
                removed_rules.append(rule)
        return removed_rules

    @staticmethod
    def detect_added_rules(current_rules, new_rules, traffic_type='ingress'):
        """Detect added rules and return the added rules dictonary"""
        added_rules = []
        # loop through new rules
        for new_rule in new_rules:
            is_added = True
            n_grants = new_rule['grants']
            n_ip_protocol = new_rule['ip_protocol'] if new_rule['ip_protocol'] else None
            n_from_port = int(new_rule['from_port']) if new_rule['from_port'] else None
            n_to_port = int(new_rule['to_port']) if new_rule['to_port'] else None
            # loop through existing rules
            for rule in current_rules:
                c_grants = rule['grants']
                c_ip_protocol = rule['ip_protocol'] if rule['ip_protocol'] else None
                c_from_port = int(rule['from_port']) if rule['from_port'] else None
                c_to_port = int(rule['to_port']) if rule['to_port'] else None
                # check if the ip protocol, from_port, and to_port match
                if c_ip_protocol == n_ip_protocol and c_from_port == n_from_port and c_to_port == n_to_port:
                    # check if the cidr_ip matches
                    if 'cidr_ip' in c_grants[0] and 'cidr_ip' in n_grants[0]:
                        if c_grants[0]['cidr_ip'] == n_grants[0]['cidr_ip']:
                            is_added = False
                    elif traffic_type == 'ingress':
                        # check if source group id matches
                        if 'src_security_group_group_id' in c_grants[0] and 'group_id' in n_grants[0]:
                            if c_grants[0]['src_security_group_group_id'] == n_grants[0]['group_id']:
                                is_added = False
                    elif traffic_type == 'egress':
                        # check if source group id matches
                        if 'src_group_id' in c_grants[0] and 'group_id' in n_grants[0]:
                            if c_grants[0]['src_group_id'] == n_grants[0]['group_id']:
                                is_added = False
            if is_added:
                added_rules.append(new_rule)
        return added_rules

    def revoke_all_rules(self, security_group=None, traffic_type='ingress'):
        if security_group is None:
            security_group = self.security_group
        if traffic_type == 'ingress':
            rules = security_group.rules
        else:
            rules = security_group.rules_egress
        for rule in rules:
            grants = rule.grants
            from_port = int(rule.from_port) if rule.from_port else None
            to_port = int(rule.to_port) if rule.to_port else None
            params = dict(
                group_id=security_group.id,
                ip_protocol=rule.ip_protocol,
                from_port=from_port,
                to_port=to_port,
            )
            for grant in grants:
                if grant.cidr_ip:
                    params.update(dict(
                        cidr_ip=grant.cidr_ip,
                    ))
                elif grant.group_id:
                    if traffic_type == 'ingress':
                        params.update(dict(
                            src_security_group_group_id=grant.group_id,
                            src_security_group_owner_id=grant.owner_id,
                        ))
                    else:
                        params.update(dict(
                            src_group_id=grant.group_id,
                        ))
                if traffic_type == 'ingress':
                    self.conn.revoke_security_group(**params)
                else:
                    self.conn.revoke_security_group_egress(**params)

    def get_protocol_by_name(self, protocol):
        ip_protocol = protocol
        if not self.check_int(ip_protocol):
            try:
                ip_protocol = socket.getprotobyname(ip_protocol)
            except:
                pass
        return ip_protocol

    @staticmethod
    def check_int(s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()
