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

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from ..forms.securitygroups import SecurityGroupForm, SecurityGroupDeleteForm, SecurityGroupsFiltersForm
from ..i18n import _
from ..models import Notification
from ..views import LandingPageView, TaggedItemView, JSONResponse
from . import boto_error_handler


class SecurityGroupsView(LandingPageView):
    TEMPLATE = '../templates/securitygroups/securitygroups.pt'

    def __init__(self, request):
        super(SecurityGroupsView, self).__init__(request)
        self.conn = self.get_connection()
        self.initial_sort_key = 'name'
        self.prefix = '/securitygroups'
        self.json_items_endpoint = self.get_json_endpoint('securitygroups_json')
        self.delete_form = SecurityGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.filters_form = SecurityGroupsFiltersForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            prefix=self.prefix,
            delete_form=self.delete_form,
            filters_form=self.filters_form,
        )

    @view_config(route_name='securitygroups', renderer=TEMPLATE)
    def securitygroups_landing(self):
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['name', 'description', 'tags']
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
                template = '{0} {1}'.format(prefix, name)
                msg = template.format(group=name)
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
    def get_rules(rules):
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
            ))
        return rules_list


class SecurityGroupsJsonView(LandingPageView):
    def __init__(self, request):
        super(SecurityGroupsJsonView, self).__init__(request)
        self.conn = self.get_connection()

    @view_config(route_name='securitygroups_json', renderer='json', request_method='GET')
    def securitygroups_json(self):
        securitygroups = []
        for securitygroup in self.filter_items(self.get_items()):
            if securitygroup.vpc_id is None:
                securitygroups.append(dict(
                    id=securitygroup.id,
                    description=securitygroup.description,
                    name=securitygroup.name,
                    owner_id=securitygroup.owner_id,
                    rules=SecurityGroupsView.get_rules(securitygroup.rules),
                    tags=TaggedItemView.get_tags_display(securitygroup.tags),
                ))
        return dict(results=securitygroups)

    def get_items(self):
        return self.conn.get_all_security_groups() if self.conn else []


class SecurityGroupView(TaggedItemView):
    """Views for single Security Group"""
    TEMPLATE = '../templates/securitygroups/securitygroup_view.pt'

    def __init__(self, request):
        super(SecurityGroupView, self).__init__(request)
        self.conn = self.get_connection()
        self.security_group = self.get_security_group()
        self.securitygroup_form = SecurityGroupForm(
            self.request, security_group=self.security_group, formdata=self.request.params or None)
        self.delete_form = SecurityGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.security_group
        self.render_dict = dict(
            security_group=self.security_group,
            security_group_name=self.escape_braces(self.security_group.name) if self.security_group else '',
            securitygroup_form=self.securitygroup_form,
            delete_form=self.delete_form,
            security_group_names=self.get_security_group_names(),
        )

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
            tags_json = self.request.params.get('tags')
            with boto_error_handler(self.request, self.request.route_path('securitygroups')):
                self.log_request(_(u"Creating security group {0}").format(name))
                new_security_group = self.conn.create_security_group(name, description)
                self.add_rules(security_group=new_security_group)
                if tags_json:
                    tags = json.loads(tags_json)
                    for tagname, tagvalue in tags.items():
                        new_security_group.add_tag(tagname, tagvalue)
                msg = _(u'Successfully created security group')
                location = self.request.route_path('securitygroup_view', id=new_security_group.id)
                if self.request.is_xhr:
                    return JSONResponse(status=200, message=msg)
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

    def get_security_group_names(self):
        groups = []
        if self.conn:
            groups = [g.name for g in self.conn.get_all_security_groups()]
        return sorted(set(groups))

    def add_rules(self, security_group=None):
        if security_group is None:
            security_group = self.security_group
        # Now add the fresh set of rules
        rules_json = self.request.params.get('rules')
        rules = json.loads(rules_json) if rules_json else []

        for rule in rules:
            ip_protocol = rule.get('ip_protocol')
            from_port = rule.get('from_port')
            to_port = rule.get('to_port')
            cidr_ip = None

            if from_port is not None and to_port is not None:
                from_port = int(from_port)
                to_port = int(to_port)
                if to_port < from_port:
                    to_port = from_port

            src_group = None
            grants = rule.get('grants', [])

            for grant in grants:
                cidr_ip = grant.get('cidr_ip')
                group_name = grant.get('name')
                owner_id = grant.get('owner_id')

            auth_args = dict(group_name=security_group.name, ip_protocol=ip_protocol, from_port=from_port, to_port=to_port, cidr_ip=cidr_ip)
            if group_name:
                auth_args['src_security_group_name'] = group_name
            if owner_id:
                auth_args['src_security_group_owner_id'] = owner_id

            self.conn.authorize_security_group(**auth_args)

    def update_rules(self):
        # Remove existing rules prior to updating, since we're doing a fresh update
        self.revoke_all_rules()
        self.add_rules()

    def revoke_all_rules(self):
        for rule in self.security_group.rules:
            grants = rule.grants
            from_port = int(rule.from_port) if rule.from_port else None
            to_port = int(rule.to_port) if rule.to_port else None
            params = dict(
                group_id=self.security_group.id,
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
                    params.update(dict(
                        src_security_group_group_id=grant.group_id,
                        src_security_group_owner_id=grant.owner_id,
                    ))
                self.conn.revoke_security_group(**params)
