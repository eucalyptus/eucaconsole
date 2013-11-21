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

from ..forms.securitygroups import SecurityGroupForm
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

    def get_security_group(self):
        group_param = self.request.matchdict.get('id')
        if group_param is None:
            return None  # If missing, we're going to return an empty security group form
        groupids = [group_param]
        security_groups = self.conn.get_all_security_groups(group_ids=groupids)
        security_group = security_groups[0] if security_groups else None
        return security_group

    @view_config(route_name='securitygroup_view', renderer='../templates/securitygroups/securitygroup_view.pt')
    def securitygroup_view(self):
        return dict(
            security_group=self.security_group,
            securitygroup_form=self.securitygroup_form,
        )

    @view_config(route_name='securitygroup_update', request_method='POST')
    def securitygroup_update(self):
        if self.securitygroup_form.validate():
            # Delete existing tags before adding updated/new ones
            for tagkey, tagvalue in self.security_group.tags.items():
                self.security_group.remove_tag(tagkey, tagvalue)
            # Insert updated/new tags
            tags_json = self.request.params.get('tags')
            tags = json.loads(tags_json) if tags_json else {}
            if tags:
                self.security_group.tags = None
                for key, value in tags.items():
                    self.security_group.add_tag(key, value)
            # Update inbound rules
            # TODO: Use security_group.authorize() to add rules.
            # TODO: wipe out rules before updating via security_group.revoke().
            location = self.request.route_url('securitygroups')
            msg = _(u'Successfully modified security group {group}')
            notification_msg = msg.format(group=self.security_group.name)
            self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return dict(
            security_group=self.security_group,
            securitygroup_form=self.securitygroup_form,
        )
