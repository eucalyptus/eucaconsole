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
Pyramid views for Eucalyptus Object Store and AWS S3 Buckets

"""
from boto.exception import S3ResponseError
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from ..i18n import _
from ..views import LandingPageView, BaseView, JSONResponse
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


class BucketsJsonView(LandingPageView):
    def __init__(self, request):
        super(BucketsJsonView, self).__init__(request)
        self.conn = self.get_connection(conn_type='s3')

    @view_config(route_name='buckets_json', renderer='json', request_method='POST')
    def buckets_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        buckets = []
        with boto_error_handler(self.request):
            items = self.get_items()
            for item in items:
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
    """Views for actions on single bucket"""
    VIEW_TEMPLATE = '../templates/buckets/bucket_view.pt'

    def __init__(self, request):
        super(BucketView, self).__init__(request)
        self.conn = self.get_connection(conn_type='s3')
        self.bucket = self.get_bucket()
        self.render_dict = dict(
            bucket=self.bucket
        )

    @view_config(route_name='bucket_view', renderer=VIEW_TEMPLATE)
    def bucket_view(self):
        return self.render_dict

    def get_bucket(self):
        try:
            bucket_name = self.request.matchdict.get('name')
            return self.conn.get_bucket(bucket_name)
        except S3ResponseError:
            return HTTPNotFound()

