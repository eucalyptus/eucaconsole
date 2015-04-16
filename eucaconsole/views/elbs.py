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
Pyramid views for Eucalyptus and AWS elbs

"""
from urllib import quote
import simplejson as json

import boto.utils

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..i18n import _
from ..forms.elbs import ELBDeleteForm, ELBsFiltersForm
from ..models import Notification
from ..views import LandingPageView, BaseView, JSONResponse
from . import boto_error_handler


class ELBsView(LandingPageView):
    def __init__(self, request):
        super(ELBsView, self).__init__(request)
        self.request = request
        self.ec2_conn = self.get_connection(conn_type="ec2")
        self.elb_conn = self.get_connection(conn_type="elb")
        self.initial_sort_key = 'name'
        self.prefix = '/elbs'
        self.filter_keys = ['name', 'dns_name']
        self.sort_keys = self.get_sort_keys()
        self.json_items_endpoint = self.get_json_endpoint('elbs_json')
        self.delete_form = ELBDeleteForm(self.request, formdata=self.request.params or None)
        self.filters_form = ELBsFiltersForm(
            self.request, cloud_type=self.cloud_type, ec2_conn=self.ec2_conn, formdata=self.request.params or None)
        search_facets = self.filters_form.facets
        self.render_dict = dict(
            filter_keys=self.filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
            delete_form=self.delete_form,
        )

    @view_config(route_name='elbs', renderer='../templates/elbs/elbs.pt')
    def elbs_landing(self):
        # sort_keys are passed to sorting drop-down
        return self.render_dict

    @view_config(route_name='elbs_delete', request_method='POST')
    def elbs_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            location = self.request.route_path('elbs')
            prefix = _(u'Unable to delete elb')
            template = u'{0} {1} - {2}'.format(prefix, name, '{0}')
            with boto_error_handler(self.request, location, template):
                self.elb_conn.delete_load_balancer(name)
                prefix = _(u'Successfully deleted elb.')
                msg = u'{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
                notification_msg = msg
                self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    @staticmethod
    def get_sort_keys():
        return [
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='created_time', name=_(u'Creation time: Oldest to Newest')),
            dict(key='-created_time', name=_(u'Creation time: Newest to Oldest')),
            dict(key='image_name', name=_(u'Image Name: A to Z')),
            dict(key='-image_name', name=_(u'Image Name: Z to A')),
            dict(key='key_name', name=_(u'Key pair: A to Z')),
            dict(key='-key_name', name=_(u'Key pair: Z to A')),
        ]


class ELBsJsonView(LandingPageView):
    """JSON response view for ELB landing page"""
    def __init__(self, request):
        super(ELBsJsonView, self).__init__(request)
        self.ec2_conn = self.get_connection()
        self.elb_conn = self.get_connection(conn_type='elb')
        with boto_error_handler(request):
            self.items = self.get_items()
            self.securitygroups = self.get_all_security_groups()

    @view_config(route_name='elbs_json', renderer='json', request_method='POST')
    def elbs_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        with boto_error_handler(self.request):
            elbs_array = []
            for elb in self.filter_items(self.items):
                # boto doesn't convert elb created_time into dtobj like it does for others
                elb.created_time = boto.utils.parse_ts(elb.created_time)
                name = elb.name
                security_groups = self.get_security_groups(elb.security_groups)
                security_groups_array = sorted({
                    'name': group.name,
                    'id': group.id,
                    'rules_count': self.get_security_group_rules_count_by_id(group.id)
                    } for group in security_groups)
                elbs_array.append(dict(
                    created_time=self.dt_isoformat(elb.created_time),
                    in_use=False,
                    dns_name=elb.dns_name,
                    name=name,
                    security_groups=security_groups_array,
                ))
            return dict(results=elbs_array)

    def get_items(self):
        return self.elb_conn.get_all_load_balancers() if self.elb_conn else []

    def get_all_security_groups(self):
        if self.ec2_conn:
            return self.ec2_conn.get_all_security_groups()
        return []

    def get_security_groups(self, groupids):
        security_groups = []
        if groupids:
            for id in groupids:
                security_group = ''
                # Due to the issue that AWS-Classic and AWS-VPC different values,
                # name and id, for .securitygroup for launch config object
                if id.startswith('sg-'):
                    security_group = self.get_security_group_by_id(id)
                else:
                    security_group = self.get_security_group_by_name(id)
                if security_group:
                    security_groups.append(security_group) 
        return security_groups

    def get_security_group_by_id(self, id):
        if self.securitygroups: 
            for sgroup in self.securitygroups:
                if sgroup.id == id:
                    return sgroup
        return ''

    def get_security_group_by_name(self, name):
        if self.securitygroups: 
            for sgroup in self.securitygroups:
                if sgroup.name == name:
                    return sgroup
        return ''

    def get_security_group_rules_count_by_id(self, id):
        if id.startswith('sg-'):
            security_group = self.get_security_group_by_id(id)
        else:
            security_group = self.get_security_group_by_name(id)
        if security_group:
            return len(security_group.rules)
        return None 

class ELBView(BaseView):
    """Views for single ELB"""
    TEMPLATE = '../templates/elbs/elb_view.pt'

    def __init__(self, request):
        super(ELBView, self).__init__(request)
        self.ec2_conn = self.get_connection()
        self.elb_conn = self.get_connection(conn_type='elb')
        with boto_error_handler(request):
            self.elb = self.get_elb()
            # boto doesn't convert elb created_time into dtobj like it does for others
            self.elb.created_time = boto.utils.parse_ts(self.elb.created_time)
        self.delete_form = ELBDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            elb=self.elb,
            elb_name=self.escape_braces(self.elb.name) if self.elb else '',
            elb_created_time=self.dt_isoformat(self.elb.created_time),
            escaped_elb_name=quote(self.elb.name),
            delete_form=self.delete_form,
            in_use=False,
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='elb_view', renderer=TEMPLATE)
    def elb_view(self):
        return self.render_dict
 
    @view_config(route_name='elb_delete', request_method='POST', renderer=TEMPLATE)
    def elb_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            location = self.request.route_path('elbs')
            prefix = _(u'Unable to delete elb')
            template = u'{0} {1} - {2}'.format(prefix, self.elb.name, '{0}')
            with boto_error_handler(self.request, location, template):
                msg = _(u"Deleting elb")
                self.log_request(u"{0} {1}".format(msg, name))
                self.elb_conn.delete_load_balancer(name)
                prefix = _(u'Successfully deleted elb.')
                msg = u'{0} {1}'.format(prefix, name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    def get_elb(self):
        if self.elb_conn:
            elb_param = self.request.matchdict.get('id')
            elbs = self.elb_conn.get_all_load_balancers(load_balancer_names=[elb_param])
            return elbs[0] if elbs else None
        return None

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
        }))


