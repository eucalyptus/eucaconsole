# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Groups

"""
import re
from urllib import urlencode

from beaker.cache import cache_region
from boto.exception import EC2ResponseError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config


from ..forms.groups import GroupForm
from ..models import Notification
from ..models import LandingPageFilter
from ..views import BaseView, LandingPageView, TaggedItemView


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
        conn = self.get_connection(conn_type="iam")
        user_choices = [] #sorted(set(item.user_name for item in conn.get_all_users().users))
        self.filter_fields = [
            LandingPageFilter(key='user', name='Users', choices=user_choices),
        ]
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['name', 'path']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Group name')),
            dict(key='path', name=_(u'Path')),
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

class GroupView(TaggedItemView):
    """Views for single Group"""
    TEMPLATE = '../templates/groups/group_view.pt'

    def __init__(self, request):
        super(GroupView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        self.group = self.get_group()
        self.group_form = GroupForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.group
        self.render_dict = dict(
            group=self.group,
            group_form=self.group_form,
        )

    def get_group(self):
        group_param = self.request.matchdict.get('name')
        group = self.conn.get_group(group_name=group_param)
        return group

    @view_config(route_name='group_view', renderer=TEMPLATE)
    def group_view(self):
        return self.render_dict
 
    @view_config(route_name='group_update', request_method='POST', renderer=TEMPLATE)
    def group_update(self):
        if self.group_form.validate():
            self.update_tags()

            location = self.request.route_url('group_view', id=self.group.id)
            msg = _(u'Successfully modified group')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return self.render_dict

