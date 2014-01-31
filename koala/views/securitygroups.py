# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS security groups

"""
import simplejson as json
import time

from boto.exception import EC2ResponseError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.response import Response
from pyramid.view import view_config

from ..forms.securitygroups import SecurityGroupForm, SecurityGroupDeleteForm
from ..models import Notification
from ..views import LandingPageView, TaggedItemView


class SecurityGroupsView(LandingPageView):
    TEMPLATE = '../templates/securitygroups/securitygroups.pt'

    def __init__(self, request):
        super(SecurityGroupsView, self).__init__(request)
        self.conn = self.get_connection()
        self.initial_sort_key = 'name'
        self.prefix = '/securitygroups'
        self.delete_form = SecurityGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            delete_form=self.delete_form,
            prefix=self.prefix,
        )

    @view_config(route_name='securitygroups', renderer=TEMPLATE)
    def securitygroups_landing(self):
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['name', 'description', 'tags']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name')),
            dict(key='description', name=_(u'Description')),
        ]
        json_items_endpoint = self.request.route_url('securitygroups_json')
        self.render_dict.update(dict(
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
        ))
        return self.render_dict

    @view_config(route_name='securitygroups_json', renderer='json', request_method='GET')
    def securitygroups_json(self):
        securitygroups = []
        for securitygroup in self.get_items():
            securitygroups.append(dict(
                id=securitygroup.id,
                description=securitygroup.description,
                name=securitygroup.name,
                owner_id=securitygroup.owner_id,
                rules=self.get_rules(securitygroup.rules),
                tags=TaggedItemView.get_tags_display(securitygroup.tags),
                vpc_id=securitygroup.vpc_id,
            ))
        return dict(results=securitygroups)

    @view_config(route_name='securitygroups_delete', request_method='POST')
    def securitygroups_delete(self):
        securitygroup_id = self.request.params.get('securitygroup_id')
        security_group = self.get_security_group(securitygroup_id)
        location = self.get_redirect_location('securitygroups')
        if security_group and self.delete_form.validate():
            name = security_group.name
            try:
                security_group.delete()
                time.sleep(1)
                prefix = _(u'Successfully deleted security group')
                template = '{0} {1}'.format(prefix, name)
                msg = template.format(group=name)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        else:
            msg = _(u'Unable to delete security group')
            self.request.session.flash(msg, queue=Notification.ERROR)
            return HTTPFound(location=location)

    def get_items(self):
        conn = self.get_connection()
        return conn.get_all_security_groups() if conn else []

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
            securitygroup_form=self.securitygroup_form,
            delete_form=self.delete_form,
            security_group_names=self.get_security_group_names(),
        )

    @view_config(route_name='securitygroup_view', renderer=TEMPLATE)
    def securitygroup_view(self):
        return self.render_dict

    @view_config(route_name='securitygroup_delete', renderer=TEMPLATE, request_method='POST')
    def securitygroup_delete(self):
        location = self.request.route_url('securitygroups')
        if self.security_group and self.delete_form.validate():
            name = self.security_group.name
            try:
                self.security_group.delete()
                prefix = _(u'Successfully deleted security group')
                msg = '{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg.format(group=name)
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='securitygroup_create', request_method='POST', renderer=TEMPLATE)
    def securitygroup_create(self):
        if self.securitygroup_form.validate():
            name = self.request.params.get('name')
            description = self.request.params.get('description')
            tags_json = self.request.params.get('tags')
            try:
                new_security_group = self.conn.create_security_group(name, description)
                self.add_rules(security_group=new_security_group)
                if tags_json:
                    tags = json.loads(tags_json)
                    for tagname, tagvalue in tags.items():
                        new_security_group.add_tag(tagname, tagvalue)
                msg = _(u'Successfully created security group')
                queue = Notification.SUCCESS
                location = self.request.route_url('securitygroup_view', id=new_security_group.id)
                status = 200
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
                location = self.request.route_url('securitygroups')
                status = getattr(err, 'status', 400)
            if self.request.is_xhr:
                resp_body = json.dumps(dict(message=msg))
                return Response(status=status, body=resp_body)
            else:
                self.request.session.flash(msg, queue=queue)
                return HTTPFound(location=location)
        if self.request.is_xhr:
            form_errors = ', '.join(self.securitygroup_form.get_errors_list())
            return Response(status=400, body=dict(message=form_errors))  # Validation failure = bad request
        else:
            self.request.error_messages = self.securitygroup_form.get_errors_list()
            return self.render_dict

    @view_config(route_name='securitygroup_update', request_method='POST', renderer=TEMPLATE)
    def securitygroup_update(self):
        if self.securitygroup_form.validate():
            # Update tags and rules
            self.update_tags()
            self.update_rules()

            location = self.request.route_url('securitygroup_view', id=self.security_group.id)
            msg = _(u'Successfully modified security group')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    def get_security_group(self, group_id=None):
        group_param = group_id or self.request.matchdict.get('id')
        if group_param is None:
            return None  # If missing, we're going to return an empty security group form
        groupids = [group_param]
        security_groups = self.conn.get_all_security_groups(group_ids=groupids)
        security_group = security_groups[0] if security_groups else None
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
                if group_name:
                    src_groups = self.conn.get_all_security_groups(groupnames=[group_name])
                    if src_groups:
                        src_group = src_groups[0]

            auth_args = dict(ip_protocol=ip_protocol, from_port=from_port, to_port=to_port, cidr_ip=cidr_ip)
            if src_group:
                auth_args['src_group'] = src_group

            security_group.authorize(**auth_args)

    def update_rules(self):
        # Remove existing rules prior to updating, since we're doing a fresh update
        self.revoke_all_rules()
        self.add_rules()

    def revoke_all_rules(self):
        for rule in self.security_group.rules:
            cidr_ip = None
            src_group = None
            grants = rule.grants
            from_port = int(rule.from_port) if rule.from_port else None
            to_port = int(rule.to_port) if rule.to_port else None

            # Grab group and cidr_ip from grants list (list of boto.ec2.securitygroup.GroupOrCIDR objects)
            group_ids = [grant.group_id for grant in grants if grant.group_id]
            if group_ids:
                src_group = self.get_security_group(group_id=group_ids[0])
            cidr_ips = [grant.cidr_ip for grant in grants if grant.cidr_ip]
            if cidr_ips:
                cidr_ip = cidr_ips[0]

            # NOTE: This will fail unless a recent version of Boto is used.
            # See https://github.com/boto/boto/issues/1729
            self.security_group.revoke(
                ip_protocol=rule.ip_protocol,
                from_port=from_port,
                to_port=to_port,
                cidr_ip=cidr_ip,
                src_group=src_group,
            )
