# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS security groups

"""

try:
    import simplejson as json
except ImportError:
    import json

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.securitygroups import SecurityGroupForm, SecurityGroupDeleteForm
from ..models import Notification
from ..views import BaseView, LandingPageView


class SecurityGroupsView(LandingPageView):
    def __init__(self, request):
        super(SecurityGroupsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/securitygroups'
        self.display_type = self.request.params.get('display', 'tableview')  # Set tableview as default

    def get_items(self):
        conn = self.get_connection()
        return conn.get_all_security_groups() if conn else []

    @view_config(route_name='securitygroups', renderer='../templates/securitygroups/securitygroups.pt')
    def securitygroups_landing(self):
        json_items_endpoint = self.request.route_url('securitygroups_json')
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['name', 'description', 'tags']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name')),
            dict(key='description', name=_(u'Description')),
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

    @view_config(route_name='securitygroups_json', renderer='json', request_method='GET')
    def securitygroups_json(self):
        securitygroups = []
        for securitygroup in self.get_items():
            rules = []
            for plist in securitygroup.rules:
                rules.append(dict(
                    from_port=plist.from_port,
                    grants=[dict(
                        name=grant.name, owner_id=grant.owner_id, group_id=grant.group_id) for grant in plist.grants],
                    to_port=plist.to_port,
                ))
            securitygroups.append(dict(
                id=securitygroup.id,
                description=securitygroup.description,
                name=securitygroup.name,
                owner_id=securitygroup.owner_id,
                rules=rules,
                tags=securitygroup.tags,
                vpc_id=securitygroup.vpc_id,
            ))
        return dict(results=securitygroups)


class SecurityGroupView(BaseView):
    """Views for actions on single Security Group"""
    def __init__(self, request):
        super(SecurityGroupView, self).__init__(request)
        self.conn = self.get_connection()
        self.security_group = self.get_security_group()
        self.securitygroup_form = SecurityGroupForm(
            self.request, security_group=self.security_group, formdata=self.request.params)
        self.delete_form = SecurityGroupDeleteForm(self.request, formdata=self.request.params)

    @view_config(route_name='securitygroup_view', renderer='../templates/securitygroups/securitygroup_view.pt')
    def securitygroup_view(self):
        return dict(
            security_group=self.security_group,
            securitygroup_form=self.securitygroup_form,
            delete_form=self.delete_form,
            security_group_names=self.get_security_group_names(),
        )

    @view_config(route_name='securitygroup_delete', request_method='POST')
    def securitygroup_delete(self):
        if self.security_group and self.delete_form.validate():
            name = self.security_group.name
            deleted = self.security_group.delete()

            if deleted:
                location = self.request.route_url('securitygroups')
                msg = _(u'Successfully deleted security group {group}')
                notification_msg = msg.format(group=name)
                self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
                return HTTPFound(location=location)

        return dict(
            security_group=self.security_group,
            securitygroup_form=self.securitygroup_form,
            security_group_names=self.get_security_group_names(),
        )

    @view_config(route_name='securitygroup_create', request_method='POST')
    def securitygroup_create(self):
        if self.securitygroup_form.validate():
            name = self.request.params.get('name')
            description = self.request.params.get('description')
            new_group = self.conn.create_security_group(name, description)
            self.add_rules(security_group=new_group)
            self.add_tags(security_group=new_group)
            location = self.request.route_url('securitygroups')
            msg = _(u'Successfully created security group {group}')
            notification_msg = msg.format(group=name)
            self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return dict(
            security_group=self.security_group,
            securitygroup_form=self.securitygroup_form,
            security_group_names=self.get_security_group_names(),
        )

    @view_config(route_name='securitygroup_update', request_method='POST')
    def securitygroup_update(self):
        if self.securitygroup_form.validate():
            # Update tags and rules
            self.update_tags()
            self.update_rules()

            location = self.request.route_url('securitygroups')
            msg = _(u'Successfully modified security group {group}')
            notification_msg = msg.format(group=self.security_group.name)
            self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return dict(
            security_group=self.security_group,
            securitygroup_form=self.securitygroup_form,
        )

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

    def add_tags(self, security_group=None):
        if security_group is None:
            security_group = self.security_group
        tags_json = self.request.params.get('tags')
        tags = json.loads(tags_json) if tags_json else {}

        for key, value in tags.items():
            security_group.add_tag(key, value)

    def update_tags(self):
        # Delete existing tags before adding new tag set
        for tagkey, tagvalue in self.security_group.tags.items():
            self.security_group.remove_tag(tagkey, tagvalue)
        self.add_tags()

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
