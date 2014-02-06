# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Groups

"""
import unicodedata
from urllib import urlencode

from boto.exception import EC2ResponseError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.groups import GroupForm, GroupUpdateForm
from ..models import Notification
from ..models import LandingPageFilter
from ..views import BaseView, LandingPageView


class GroupsView(LandingPageView):
    TEMPLATE = '../templates/groups/groups.pt'

    def __init__(self, request):
        super(GroupsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/groups'

    @view_config(route_name='groups', renderer=TEMPLATE)
    def groups_landing(self):
        json_items_endpoint = self.request.route_url('groups_json')
        if self.request.GET:
            json_items_endpoint += '?{params}'.format(params=urlencode(self.request.GET))
        user_choices = []  # sorted(set(item.user_name for item in conn.get_all_users().users))
        self.filter_fields = [
            LandingPageFilter(key='user', name='Users', choices=user_choices),
        ]
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['path', 'group_name', 'group_id', 'arn']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Group name')),
            dict(key='path', name=_(u'Path')),
        ]

        return dict(
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
        )


class GroupsJsonView(BaseView):
    """Groups returned as JSON"""
    @view_config(route_name='groups_json', renderer='json', request_method='GET')
    def groups_json(self):
        # TODO: take filters into account??
        groups = []
        for group in self.get_items():
            groups.append(dict(
                path=group.path,
                group_name=group.group_name,
                group_id=group.group_id,
                arn=group.arn,
            ))
        return dict(results=groups)

    def get_items(self):
        conn = self.get_connection(conn_type="iam")
        try:
            return conn.get_all_groups().groups
        except EC2ResponseError as exc:
            return BaseView.handle_403_error(exc, request=self.request)


class GroupView(BaseView):
    """Views for single Group"""
    TEMPLATE = '../templates/groups/group_view.pt'

    def __init__(self, request):
        super(GroupView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        self.group = self.get_group()
        self.group_route_id = self.request.matchdict.get('name')
        self.group_users = self.get_users_array(self.group)
        self.all_users = self.get_all_users_array()
        self.group_form = GroupForm(self.request, group=self.group, formdata=self.request.params or None)
        self.group_update_form = GroupUpdateForm(self.request, group=self.group, formdata=self.request.params or None)
        self.render_dict = dict(
            group=self.group,
            group_route_id=self.group_route_id,
            group_users=self.group_users,
            all_users=self.all_users,
            group_form=self.group_form,
            group_update_form=self.group_update_form,
        )

    def get_group(self):
        group_param = self.request.matchdict.get('name')
        # Return None if the request is to create new group. Prob. No groupname "new" can be created
        if group_param == "new" or group_param is None:
            return None
        group = []
        if self.conn:
            group = self.conn.get_group(group_name=group_param)
        return group

    def get_users_array(self, group):
        if group is None:
            return []
        users = [u.user_name.encode('ascii', 'ignore') for u in group.users]
        return users

    def get_all_users_array(self):
        group_param = self.request.matchdict.get('name')
        if group_param == "new" or group_param is None:
            return None
        users = []
        # Group's path to be used ?
        if self.conn:
            users = [u.user_name.encode('ascii', 'ignore') for u in self.conn.get_all_users().users]
        return users

    @view_config(route_name='group_view', renderer=TEMPLATE)
    def group_view(self):
        return self.render_dict
 
    @view_config(route_name='group_create', request_method='POST', renderer=TEMPLATE)
    def group_create(self):
        if self.group_form.validate():
            new_group_name = self.request.params.get('group_name') 
            new_path = self.request.params.get('path')
            try:
                self.conn.create_group(group_name=new_group_name, path=new_path)
                msg_template = _(u'Successfully created group {group}')
                msg = msg_template.format(group=new_group_name)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            location = self.request.route_url('group_view', name=new_group_name)
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='group_update', request_method='POST', renderer=TEMPLATE)
    def group_update(self):
        if self.group_update_form.validate():
            new_users = self.request.params.getall('input-users-select')
            if new_users is not None:
                self.group_update_users( self.group.group_name, new_users)
            new_group_name = self.request.params.get('group_name') if self.group.group_name != self.request.params.get('group_name') else None
            new_path = self.request.params.get('path') if self.group.path != self.request.params.get('path') else None
            this_group_name = new_group_name if new_group_name is not None else self.group.group_name
            try:
                self.conn.update_group(self.group.group_name, new_group_name=new_group_name, new_path=new_path)
                msg_template = _(u'Successfully modified group {group}')
                msg = msg_template.format(group=this_group_name)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            location = self.request.route_url('group_view', name=this_group_name)
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)

        return self.render_dict

    def group_update_users(self, group_name, new_users):
        new_users = [u.encode('ascii', 'ignore') for u in new_users]

        for new_user in new_users:
            isNew = True
            for user in self.group_users:
                if user == new_user:
                    isNew = False
            if isNew:
                self.conn.add_user_to_group(group_name, new_user)

        for user in self.group_users:
            isDeleted = True
            for new_user in new_users:
                if user == new_user:
                    isDeleted = False
            if isDeleted:
                self.conn.remove_user_from_group(group_name, user)

        return 





