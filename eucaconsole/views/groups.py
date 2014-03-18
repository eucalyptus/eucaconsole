# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Groups

"""
from datetime import datetime
from dateutil import parser
import simplejson as json
from urllib import urlencode

from boto.exception import BotoServerError
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.groups import GroupForm, GroupUpdateForm, DeleteGroupForm
from ..models import Notification
from ..views import BaseView, LandingPageView, JSONResponse
from . import boto_error_handler


class GroupsView(LandingPageView):
    TEMPLATE = '../templates/groups/groups.pt'

    def __init__(self, request):
        super(GroupsView, self).__init__(request)
        self.initial_sort_key = 'group_name'
        self.prefix = '/groups'

    @view_config(route_name='groups', renderer=TEMPLATE)
    def groups_landing(self):
        json_items_endpoint = self.request.route_path('groups_json')
        if self.request.GET:
            json_items_endpoint += '?{params}'.format(params=urlencode(self.request.GET))
        user_choices = []  # sorted(set(item.user_name for item in conn.get_all_users().users))
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['path', 'group_name', 'group_id', 'arn']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='group_name', name=_(u'Group name: A to Z')),
            dict(key='-group_name', name=_(u'Group name: Z to A')),
        ]

        return dict(
            filter_fields=False,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
            delete_form=DeleteGroupForm(self.request),
        )


class GroupsJsonView(BaseView):
    """Groups returned as JSON"""
    def __init__(self, request):
        super(GroupsJsonView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")

    @view_config(route_name='groups_json', renderer='json', request_method='GET')
    def groups_json(self):
        # TODO: take filters into account??
        groups = []
        for group in self.get_items():
            policies = []
            try:
                policies = self.conn.get_all_group_policies(group_name=group.group_name)
                policies = policies.policy_names
            except BotoServerError as exc:
                pass
            user_count = 0
            try:
                group = self.conn.get_group(group_name=group.group_name)
                user_count=len(group.users) if hasattr(group, 'users') else 0
            except BotoServerError as exc:
                pass
            groups.append(dict(
                path=group.path,
                group_name=group.group_name,
                create_date=group.create_date,
                user_count=user_count,
                policy_count=len(policies),
            ))
        return dict(results=groups)

    def get_items(self):
        with boto_error_handler(self.request):
            return self.conn.get_all_groups().groups


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
        self.delete_form = DeleteGroupForm(self.request, formdata=self.request.params)
        create_date = parser.parse(self.group.create_date) if self.group else datetime.now()
        self.render_dict = dict(
            group=self.group,
            group_create_date=create_date,
            group_route_id=self.group_route_id,
            group_users=self.group_users,
            all_users=self.all_users,
            group_form=self.group_form,
            group_update_form=self.group_update_form,
            delete_form=self.delete_form,
        )

    def get_group(self):
        group_param = self.request.matchdict.get('name')
        # Return None if the request is to create new group. Prob. No groupname "new" can be created
        if group_param == "new" or group_param is None:
            return None
        group = None
        try:
            group = self.conn.get_group(group_name=group_param)
        except BotoServerError as err:
            pass
        return group

    @staticmethod
    def get_users_array(group):
        if group is None:
            return []
        users = [u.user_name.encode('ascii', 'ignore') for u in group.users]
        return users

    def get_all_users_array(self):
        group_param = self.request.matchdict.get('name')
        if group_param == "new" or group_param is None:
            return []
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
            location = self.request.route_path('group_view', name=new_group_name)
            with boto_error_handler(self.request, location):
                self.conn.create_group(group_name=new_group_name, path=new_path)
                msg_template = _(u'Successfully created group {group}')
                msg = msg_template.format(group=new_group_name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='group_update', request_method='POST', renderer=TEMPLATE)
    def group_update(self):
        if self.group_update_form.validate():
            new_users = self.request.params.getall('input-users-select')
            group_name_param = self.request.params.get('group_name')
            new_group_name = group_name_param if self.group.group_name != group_name_param else None
            new_path = self.request.params.get('path') if self.group.path != self.request.params.get('path') else None
            this_group_name = new_group_name if new_group_name is not None else self.group.group_name
            if new_users is not None:
                self.group_update_users( self.group.group_name, new_users)
            location = self.request.route_path('group_view', name=this_group_name)
            if new_group_name is not None or new_path is not None:
                with boto_error_handler(self.request, location):
                    self.group_update_name_and_path(new_group_name, new_path)
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='group_delete', request_method='POST')
    def group_delete(self):
        if not self.delete_form.validate():
            return JSONResponse(status=400, message="missing CSRF token")
        location = self.request.route_path('groups')
        if self.group is None:
            raise HTTPNotFound()
        with boto_error_handler(self.request, location):
            params = {'GroupName': self.group.group_name, 'IsRecursive': 'true'}
            self.conn.get_response('DeleteGroup', params)
            msg = _(u'Successfully deleted group')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
        return HTTPFound(location=location)

    def group_update_name_and_path(self, new_group_name, new_path):
        this_group_name = new_group_name if new_group_name is not None else self.group.group_name
        self.conn.update_group(self.group.group_name, new_group_name=new_group_name, new_path=new_path)
        msg_template = _(u'Successfully modified group {group}')
        msg = msg_template.format(group=this_group_name)
        self.request.session.flash(msg, queue=Notification.SUCCESS)
        return

    def group_update_users(self, group_name, new_users):
        new_users = [u.encode('ascii', 'ignore') for u in new_users]

        self.group_add_new_users(group_name, new_users)
        self.group_remove_deleted_users(group_name, new_users)

        return 

    def group_add_new_users(self, group_name, new_users):
        success_msg = ''
        error_msg = ''
        for new_user in new_users:
            is_new = True
            for user in self.group_users:
                if user == new_user:
                    is_new = False
            if is_new:
                (msg, queue) = self.group_add_user(group_name, new_user)
                if queue is Notification.SUCCESS:
                    success_msg += msg + " "
                else:
                    error_msg += msg + " "

        if success_msg != '':
            self.request.session.flash(success_msg, queue=Notification.SUCCESS)
        if error_msg != '':
            self.request.session.flash(error_msg, queue=Notification.ERROR)

        return

    def group_remove_deleted_users(self, group_name, new_users):
        success_msg = ''
        error_msg = ''
        for user in self.group_users:
            is_deleted = True
            for new_user in new_users:
                if user == new_user:
                    is_deleted = False
            if is_deleted:
                (msg, queue) = self.group_remove_user(group_name, user)
                if queue is Notification.SUCCESS:
                    success_msg += msg + " "
                else:
                    error_msg += msg + " "

        if success_msg != '':
            self.request.session.flash(success_msg, queue=Notification.SUCCESS)
        if error_msg != '':
            self.request.session.flash(error_msg, queue=Notification.ERROR)

        return

    def group_add_user(self, group_name, user):
        try:
            self.conn.add_user_to_group(group_name, user)
            msg_template = _(u'Successfully added user {user}')
            msg = msg_template.format(user=user)
            queue = Notification.SUCCESS
        except BotoServerError as err:
            msg = err.message
            queue = Notification.ERROR

        return msg, queue

    def group_remove_user(self, group_name, user):
        try:
            self.conn.remove_user_from_group(group_name, user)
            msg_template = _(u'Successfully removed user {user}')
            msg = msg_template.format(user=user)
            queue = Notification.SUCCESS
        except BotoServerError as err:
            msg = err.message
            queue = Notification.ERROR

        return msg, queue

    @view_config(route_name='group_policies_json', renderer='json', request_method='GET')
    def group_policies_json(self):
        """Return group policies list"""
        with boto_error_handler(self.request):
            policies = self.conn.get_all_group_policies(group_name=self.group.group_name)
            return dict(results=policies.policy_names)

    @view_config(route_name='group_policy_json', renderer='json', request_method='GET')
    def group_policy_json(self):
        """Return group policies list"""
        with boto_error_handler(self.request):
            policy_name = self.request.matchdict.get('policy')
            policy = self.conn.get_group_policy(group_name=self.group.group_name, policy_name=policy_name)
            parsed = json.loads(policy.policy_document)
            return dict(results=json.dumps(parsed, indent=2))

    @view_config(route_name='group_update_policy', request_method='POST', renderer='json')
    def group_update_policy(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        # calls iam:PutGroupPolicy
        policy = self.request.matchdict.get('policy')
        with boto_error_handler(self.request):
            policy_text = self.request.params.get('policy_text')
            result = self.conn.put_group_policy(
                group_name=self.group.group_name, policy_name=policy, policy_json=policy_text)
            return dict(message=_(u"Successfully updated group policy"), results=result)

    @view_config(route_name='group_delete_policy', request_method='POST', renderer='json')
    def group_delete_policy(self):
        if not self.is_csrf_valid():
            return JSONResponse(status=400, message="missing CSRF token")
        # calls iam:DeleteGroupPolicy
        policy = self.request.matchdict.get('policy')
        with boto_error_handler(self.request):
            result = self.conn.delete_group_policy(group_name=self.group.group_name, policy_name=policy)
            return dict(message=_(u"Successfully deleted group policy"), results=result)

