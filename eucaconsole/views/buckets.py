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
import mimetypes

from boto.s3.prefix import Prefix
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from ..forms.buckets import BucketDetailsForm, SharingPanelForm
from ..i18n import _
from ..views import BaseView, LandingPageView, JSONResponse
from . import boto_error_handler


DELIMITER = '/'


class BucketsView(LandingPageView):
    """Views for Buckets landing page"""
    VIEW_TEMPLATE = '../templates/buckets/buckets.pt'

    def __init__(self, request):
        super(BucketsView, self).__init__(request)
        # self.items = self.get_items()  # Only need this when filters are displayed on the landing page
        self.prefix = '/buckets'
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
            filter_keys=['bucket_name'],
            bucket_objects_count_url=self.request.route_path('bucket_objects_count_json', name='_name_')
        )
        return self.render_dict


class BucketsJsonView(BaseView):
    def __init__(self, request):
        super(BucketsJsonView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')

    @view_config(route_name='buckets_json', renderer='json', request_method='POST')
    def buckets_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        buckets = []
        with boto_error_handler(self.request):
            items = self.get_items()
            for item in items:
                bucket_name = item.name
                buckets.append(dict(
                    bucket_name=bucket_name,
                    contents_url=self.request.route_path('bucket_contents', subpath=bucket_name),
                    details_url=self.request.route_path('bucket_details', name=bucket_name),
                    owner='',  # TODO: pull in bucket owner if possible
                    versioning=BucketDetailsView.get_versioning_status(item),
                    creation_date=item.creation_date
                ))
            return dict(results=buckets)

    @view_config(route_name='bucket_objects_count_json', renderer='json')
    def bucket_object_counts_json(self):
        bucket = BucketContentsView.get_bucket(self.request, self.s3_conn) if self.s3_conn else []
        results = dict(
            object_count=len(tuple(bucket.list())),
        )
        return dict(results=results)

    def get_items(self):
        return self.s3_conn.get_all_buckets() if self.s3_conn else []


class BucketContentsView(LandingPageView):
    """Views for actions on single bucket"""
    VIEW_TEMPLATE = '../templates/buckets/bucket_contents.pt'

    def __init__(self, request):
        super(BucketContentsView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')
        self.prefix = '/buckets'
        self.bucket_name = self.get_bucket_name(request)
        self.subpath = request.subpath
        self.render_dict = dict(
            bucket_name=self.bucket_name,
        )

    @view_config(route_name='bucket_contents', renderer=VIEW_TEMPLATE)
    def bucket_contents(self):
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='-size', name=_(u'Size: Largest to smallest')),
            dict(key='size', name=_(u'Size: Smallest to largest')),
        ]
        json_route_path = self.request.route_path('bucket_contents', name=self.bucket_name, subpath=self.subpath)
        self.render_dict.update(
            prefix=self.prefix,
            initial_sort_key='name',
            json_items_endpoint=self.get_json_endpoint(json_route_path, path=True),
            sort_keys=self.sort_keys,
            filter_fields=False,
            filter_keys=['name'],
        )
        return self.render_dict

    @staticmethod
    def get_bucket_name(request):
        subpath = request.matchdict.get('subpath')
        if len(subpath):
            return subpath[0]

    @staticmethod
    def get_unprefixed_key_name(key_name):
        if DELIMITER not in key_name:
            return key_name
        if DELIMITER in key_name:
            key_arr = key_name.split(DELIMITER)
            if key_name.endswith(DELIMITER):
                return key_arr[-2]
            return key_arr[-1]
        return key_name

    @staticmethod
    def get_bucket(request, s3_conn, bucket_name=None):
        with boto_error_handler(request):
            subpath = request.matchdict.get('subpath')
            bucket_name = bucket_name or request.matchdict.get('name') or subpath[0]
            bucket = s3_conn.lookup(bucket_name, validate=False) if bucket_name else None
            if bucket is None:
                return HTTPNotFound()
            return bucket

    @staticmethod
    def get_icon_class(key_name):
        """Get the icon class from the mime type of an object based on its key name
        :returns a string that maps to a Foundation Icon Fonts 3 class name
        :rtype str
        See http://zurb.com/playground/foundation-icon-fonts-3

        """
        mime_type = mimetypes.guess_type(key_name)[0]
        if mime_type is None:
            return ''
        if '/' in key_name:
            key_name = key_name.split('/')[-1]
            mime_type = mimetypes.guess_type(key_name)[0]
        if 'zip' in mime_type:
            return 'fi-archive'
        if 'pdf' in mime_type:
            return 'fi-page-pdf'
        if '/' in mime_type:
            mime_type = mime_type.split('/')[0]
        icon_mapping = {
            'image': 'fi-photo',
            'text': 'fi-page',
            'video': 'fi-video',
        }
        return icon_mapping.get(mime_type, 'fi-page')


class BucketContentsJsonView(BaseView):
    def __init__(self, request):
        super(BucketContentsJsonView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')
        self.bucket = BucketContentsView.get_bucket(request, self.s3_conn)
        self.bucket_name = self.bucket.name
        self.subpath = request.subpath

    @view_config(route_name='bucket_contents', renderer='json', request_method='POST', xhr=True)
    def bucket_contents_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        items = []
        list_prefix = '{0}/'.format(DELIMITER.join(self.subpath[1:])) if len(self.subpath) > 1 else ''
        params = dict(delimiter=DELIMITER)
        if list_prefix:
            params.update(dict(prefix=list_prefix))
        bucket_items = self.bucket.list(**params)

        for key in bucket_items:
            if self.skip_item(key):
                continue
            if isinstance(key, Prefix):
                item = dict(
                    size=0,
                    is_folder=True,
                    last_modified=None,
                    icon='fi-folder',
                )
            else:
                item = dict(
                    size=key.size,
                    is_folder=False,
                    last_modified=key.last_modified,
                    icon=BucketContentsView.get_icon_class(key.name),
                )
            item.update(dict(
                name=BucketContentsView.get_unprefixed_key_name(key.name),
                absolute_path=self.get_absolute_path(key.name),
            ))
            items.append(item)
        return dict(results=items)

    def get_absolute_path(self, key_name):
        return '/bucketcontents/{0}/{1}'.format(self.bucket_name, key_name)

    def skip_item(self, key):
        """Skip item if it contains a folder path that doesn't match the current request subpath"""
        # Test if request subpath matches current folder
        if DELIMITER in key.name:
            joined_subpath = DELIMITER.join(self.subpath[1:])
            if key.name == '{0}{1}'.format(joined_subpath, DELIMITER):
                return True
            else:
                return False
        return False


class BucketDetailsView(BaseView):
    """Views for Bucket details"""
    VIEW_TEMPLATE = '../templates/buckets/bucket_details.pt'

    def __init__(self, request):
        super(BucketDetailsView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')
        self.bucket = BucketContentsView.get_bucket(request, self.s3_conn)
        self.details_form = BucketDetailsForm(request)
        self.sharing_form = SharingPanelForm(request)
        self.render_dict = dict(
            details_form=self.details_form,
            sharing_form=self.sharing_form,
        )

    @view_config(route_name='bucket_details', renderer=VIEW_TEMPLATE)
    def bucket_details(self):
        self.render_dict.update(
            bucket=self.bucket,
            bucket_creation_date=self.get_bucket_creation_date(),
            bucket_name=self.bucket.name,
            owner=self.get_bucket_owner_name(self.bucket),
            versioning_status=self.get_versioning_status(self.bucket),
            logging_status=self.get_logging_status(),
            bucket_contents_url=self.request.route_path('bucket_contents', subpath=self.bucket.name),
            bucket_objects_count_url=self.request.route_path('bucket_objects_count_json', name=self.bucket.name)
        )
        return self.render_dict

    def get_logging_status(self):
        """Returns the logging status as a dict, with the logs URL included for templates"""
        if self.cloud_type == 'euca':  # TODO: Remove this block when Euca supports bucket logging
            return dict(enabled=False)
        if self.bucket:
            status = self.bucket.get_logging_status()
            logging_enabled = hasattr(status, 'LoggingEnabled')
            logging_prefix = getattr(status, 'prefix', '')
            if logging_prefix and DELIMITER in logging_prefix:
                logging_prefix = '{0}/'.format(logging_prefix.split(DELIMITER)[0])
            logging_subpath = '{0}/{1}'.format(self.bucket.name, logging_prefix)
            return dict(
                enabled=logging_enabled,
                logs_prefix=logging_prefix,
                logs_url=self.request.route_path('bucket_contents', subpath=logging_subpath)
            )

    def get_bucket_creation_date(self):
        """Due to limitations in the AWS API, the creation date is missing when fetching a single bucket,
           so as a workaround we need to fetch all buckets and match the current one to get the creation timestamp.
           FIXME: Remove this hack if/when we have bucket.creation_date available via s3_conn.get_bucket()
        """
        buckets = self.s3_conn.get_all_buckets() if self.s3_conn else []
        matched_bucket = [bucket for bucket in buckets if bucket.name == self.bucket.name]
        if matched_bucket:
            return getattr(matched_bucket[0], 'creation_date', None)

    @staticmethod
    def get_bucket_owner_name(bucket):
        if bucket:
            bucket_acl = bucket.get_acl()
            owner_obj = bucket_acl.owner
            if owner_obj:
                return owner_obj.display_name

    @staticmethod
    def get_versioning_status(bucket):
        if bucket:
            # TODO: get_versioning_status always seems to return an empty dict.  May be a boto bug
            status = bucket.get_versioning_status()
            return status.get('Versioning', 'Disabled')

