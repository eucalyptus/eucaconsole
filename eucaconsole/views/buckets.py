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
Pyramid views for Eucalyptus and AWS Elastic IP Addresses

"""
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..i18n import _
from ..models import Notification
from ..views import LandingPageView, TaggedItemView, BaseView, JSONResponse
from . import boto_error_handler


class BucketsView(LandingPageView):
    """Views for Buckets landing page"""
    VIEW_TEMPLATE = '../templates/buckets/buckets.pt'

    def __init__(self, request):
        super(BucketsView, self).__init__(request)
        # self.items = self.get_items()  # Only need this when filters are displayed on the landing page
        self.prefix = '/buckets'
        self.conn = self.get_connection(conn_type="s3")
        self.location = self.get_redirect_location('buckets')
        self.render_dict = dict(
            prefix=self.prefix,
        )

    @view_config(route_name='buckets', renderer=VIEW_TEMPLATE)
    def buckets_landing(self):
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='bucket_name', name=_(u'Bucket name: A to Z')),
            dict(key='-bucket_name', name=_(u'Bucket name: Z to A')),
        ]
        self.render_dict.update(
            initial_sort_key='bucket_name',
            json_items_endpoint=self.get_json_endpoint('buckets_json'),
            sort_keys=self.sort_keys,
            filter_fields=False,
            filter_keys=['name'],
        )
        return self.render_dict

    #@view_config(route_name='ipaddresses_associate', request_method="POST")
    def ipaddresses_associate(self):
        if self.associate_form.validate():
            instance_id = self.request.params.get('instance_id')
            public_ip = self.request.params.get('public_ip')
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Associating ElasticIP {0} with instance {1}").format(public_ip, instance_id))
                elastic_ip = self.get_elastic_ip(public_ip)
                elastic_ip.associate(instance_id)
                template = _(u'Successfully associated IP {ip} with instance {instance}')
                msg = template.format(ip=elastic_ip.public_ip, instance=instance_id)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            msg = _(u'Unable to associate IP with instance')
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)


class BucketsJsonView(LandingPageView):
    def __init__(self, request):
        super(BucketsJsonView, self).__init__(request)
        self.conn = self.get_connection(conn_type="s3")

    @view_config(route_name='buckets_json', renderer='json', request_method='POST')
    def buckets_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        buckets = []
        with boto_error_handler(self.request):
            items = self.get_items()
            for item in items:
                #import pdb; pdb.set_trace()
                buckets.append(dict(
                    bucket_name=item.name,
                    object_count=0,
                    owner='me',
                    creation_date=item.creation_date
                ))
            return dict(results=buckets)

    def get_items(self):
        return self.conn.get_all_buckets() if self.conn else []


class BucketView(BaseView):
    """Views for actions on single IP Address"""
    VIEW_TEMPLATE = '../templates/ipaddresses/ipaddress_view.pt'

    def __init__(self, request):
        super(IPAddressView, self).__init__(request)
        self.conn = self.get_connection()
        self.elastic_ip = self.get_elastic_ip()
        self.instance = self.get_instance()
        self.associate_form = AssociateIPForm(self.request, conn=self.conn, formdata=self.request.params or None)
        self.disassociate_form = DisassociateIPForm(self.request, formdata=self.request.params or None)
        self.release_form = ReleaseIPForm(self.request, formdata=self.request.params or None)
        if self.elastic_ip:
            self.elastic_ip.instance_name = ''
            if self.instance:
                self.elastic_ip.instance_name = TaggedItemView.get_display_name(self.instance)
        self.render_dict = dict(
            eip=self.elastic_ip,
            associate_form=self.associate_form,
            disassociate_form=self.disassociate_form,
            release_form=self.release_form,
        )

    #@view_config(route_name='ipaddress_view', renderer=VIEW_TEMPLATE)
    def ipaddress_view(self):
        return self.render_dict

    #@view_config(route_name='ipaddress_associate', request_method="POST")
    def ipaddress_associate(self):
        if self.associate_form.validate():
            instance_id = self.request.params.get('instance_id')
            location = self.request.route_path('ipaddresses')
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Associating ElasticIP {0} with instance {1}").format(self.elastic_ip, instance_id))
                self.elastic_ip.associate(instance_id)
                msg = _(u'Successfully associated IP {ip} with instance {instance}')
                notification_msg = msg.format(ip=self.elastic_ip.public_ip, instance=instance_id)
                self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

