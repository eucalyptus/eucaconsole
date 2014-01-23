# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Users

"""
import re
from urllib import urlencode

from beaker.cache import cache_region
from boto.exception import EC2ResponseError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config


from ..forms.users import UserForm
from ..models import Notification
from ..models import LandingPageFilter
from ..views import BaseView, LandingPageView, TaggedItemView


class UsersView(LandingPageView):
    TEMPLATE = '../templates/users/users.pt'

    def __init__(self, request):
        super(UsersView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/users'

    @view_config(route_name='users', renderer=TEMPLATE)
    def users_landing(self):
        json_items_endpoint = self.request.route_url('users_json')
        if self.request.GET:
            json_items_endpoint += '?{params}'.format(params=urlencode(self.request.GET))
        conn = self.get_connection(conn_type="iam")
        group_choices = sorted(set(conn.get_all_groups().groups))
        self.filter_fields = [
            LandingPageFilter(key='group', name='Groups', choices=group_choices),
        ]
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['user_name', 'user_id', 'arn', 'path']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='user_id', name='ID'),
            dict(key='name', name=_(u'User name')),
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


class UsersJsonView(BaseView):
    """Users returned as JSON"""
    @view_config(route_name='users_json', renderer='json', request_method='GET')
    def users_json(self):
    # TODO: take filters into account??
        users = []
        for user in self.get_items():
            users.append(dict(
                path=user.path,
                user_name=user.user_name,
                user_id=user.user_id,
                arn=user.arn,
            ))
        return dict(results=users)

    def get_items(self):
        conn = self.get_connection(conn_type="iam")
        try:
            return conn.get_all_users().users
        except EC2ResponseError as exc:
            return BaseView.handle_403_error(exc, request=self.request)

class UserView(TaggedItemView):
    """Views for single User"""
    TEMPLATE = '../templates/users/user_view.pt'

    def __init__(self, request):
        super(UserView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        self.user = self.get_user()
        self.user_form = UserForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.user
        self.render_dict = dict(
            user=self.user,
            user_form=self.user_form,
        )

    def get_user(self):
        user_param = self.request.matchdict.get('name')
        user = self.conn.get_user(user_name=user_param)
        return user

    @view_config(route_name='user_view', renderer=TEMPLATE)
    def user_view(self):
        return self.render_dict
 
    @view_config(route_name='user_update', request_method='POST', renderer=TEMPLATE)
    def user_update(self):
        if self.user_form.validate():
            self.update_tags()

            location = self.request.route_url('user_view', id=self.user.id)
            msg = _(u'Successfully modified user')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return self.render_dict

