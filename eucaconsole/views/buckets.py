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
import simplejson as json

from boto.s3.acl import ACL, Grant, Policy
from boto.s3.prefix import Prefix
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config

from ..forms.buckets import (
    BucketDetailsForm, BucketItemDetailsForm, SharingPanelForm, BucketUpdateVersioningForm, MetadataForm)
from ..i18n import _
from ..models import Notification
from ..views import BaseView, LandingPageView, JSONResponse
from . import boto_error_handler


DELIMITER = '/'
BUCKET_ITEM_URL_EXPIRES = 300  # Link to item expires in ___ seconds (after page load)


class BucketsView(LandingPageView):
    """Views for Buckets landing page"""
    VIEW_TEMPLATE = '../templates/buckets/buckets.pt'

    def __init__(self, request):
        super(BucketsView, self).__init__(request)
        # self.items = self.get_items()  # Only need this when filters are displayed on the landing page
        self.prefix = '/buckets'
        self.location = self.get_redirect_location('buckets')
        self.sort_keys = [
            dict(key='bucket_name', name=_(u'Bucket name: A to Z')),
            dict(key='-bucket_name', name=_(u'Bucket name: Z to A')),
        ]
        self.render_dict = dict(
            prefix=self.prefix,
            versioning_form=BucketUpdateVersioningForm(request, formdata=self.request.params or None),
            update_versioning_url=request.route_path('bucket_update_versioning', name='_name_'),
            initial_sort_key='bucket_name',
            json_items_endpoint=self.get_json_endpoint('buckets_json'),
            sort_keys=self.sort_keys,
            filter_fields=False,
            filter_keys=['bucket_name'],
            bucket_objects_count_url=self.request.route_path('bucket_objects_count_versioning_json', name='_name_'),
        )

    @view_config(route_name='buckets', renderer=VIEW_TEMPLATE)
    def buckets_landing(self):
        # sort_keys are passed to sorting drop-down
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
                    creation_date=item.creation_date,
                ))
            return dict(results=buckets)

    @view_config(route_name='bucket_objects_count_versioning_json', renderer='json')
    def bucket_objects_count_versioning_json(self):
        bucket = BucketContentsView.get_bucket(self.request, self.s3_conn) if self.s3_conn else []
        results = dict(
            object_count=len(tuple(bucket.list())),
            versioning_status=BucketDetailsView.get_versioning_status(bucket),
        )
        return dict(results=results)

    def get_items(self):
        return self.s3_conn.get_all_buckets() if self.s3_conn else []


class BucketXHRView(BaseView):
    def __init__(self, request):
        super(BucketXHRView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')
        self.bucket_name = request.matchdict.get('name')

    @view_config(route_name='bucket_delete_keys', renderer='json', request_method='POST')
    def bucket_delete_keys(self):
        """
        Deletes keys from a bucket, attempting to do as many as possible, reporting errors back at the end.
        """
        keys = self.request.params.get('keys')
        bucket = self.s3_conn.get_bucket(self.bucket_name)
        errors = []
        self.log_request(_(u"Deleting keys from {0} : {1}").format(self.bucket_name, keys))
        for k in keys.split(','):
            key = bucket.get_key(k)
            try:
                pass #key.delete()
            except BotoServerError as err:
                self.log_request("Couldn't delete "+k+":"+err.message)
                errors.append(k)
        if len(errors) == 0:
            return dict(message=_(u"Successfully deleted all keys."))
        else:
            return dict(message=_(u"Failed to delete all keys."), errors=errors)


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
            key_prefix='/'.join(self.subpath[1:]) if len(self.subpath) > 0 else '',
            display_path='/'.join(self.subpath),
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
        subpath = request.matchdict.get('subpath')
        bucket_name = bucket_name or request.matchdict.get('name') or subpath[0]
        bucket = s3_conn.lookup(bucket_name, validate=False) if bucket_name else None
        if bucket is None:
            raise HTTPNotFound()
        return bucket

    @staticmethod
    def get_item_download_url(bucket_item):
        if bucket_item.size == 0 and DELIMITER in bucket_item.name:
            return ''  # skip if folder
        item_name = BucketContentsView.get_unprefixed_key_name(bucket_item.name)
        return bucket_item.generate_url(
            expires_in=BUCKET_ITEM_URL_EXPIRES,
            response_headers={'response-content-disposition': 'attachment; filename={0}'.format(item_name)},
        )

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
            if isinstance(key, Prefix):  # Is folder
                item = dict(
                    size=0,
                    is_folder=True,
                    last_modified=None,
                    icon='fi-folder',
                    download_url='',
                )
            else:  # Is not folder
                item = dict(
                    size=key.size,
                    is_folder=False,
                    last_modified=key.last_modified,
                    icon=BucketContentsView.get_icon_class(key.name),
                    download_url=BucketContentsView.get_item_download_url(key),
                )
            item.update(dict(
                name=BucketContentsView.get_unprefixed_key_name(key.name),
                absolute_path=self.get_absolute_path(key.name),
                details_url=self.request.route_path('bucket_item_details', name=self.bucket.name, subpath=key.name),
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
        with boto_error_handler(request):
            self.bucket = BucketContentsView.get_bucket(request, self.s3_conn)
            self.bucket_acl = self.bucket.get_acl() if self.bucket else None
        self.details_form = BucketDetailsForm(request, formdata=self.request.params or None)
        self.sharing_form = SharingPanelForm(
            request, bucket_object=self.bucket, sharing_acl=self.bucket_acl, formdata=self.request.params or None)
        self.versioning_form = BucketUpdateVersioningForm(request, formdata=self.request.params or None)
        self.versioning_status = self.get_versioning_status(self.bucket)
        self.render_dict = dict(
            details_form=self.details_form,
            sharing_form=self.sharing_form,
            versioning_form=self.versioning_form,
            bucket=self.bucket,
            bucket_creation_date=self.get_bucket_creation_date(self.s3_conn, self.bucket.name),
            bucket_name=self.bucket.name,
            owner=self.get_bucket_owner_name(self.bucket_acl),
            versioning_status=self.versioning_status,
            update_versioning_action=self.get_versioning_update_action(self.versioning_status),
            logging_status=self.get_logging_status(),
            bucket_contents_url=self.request.route_path('bucket_contents', subpath=self.bucket.name),
            bucket_objects_count_url=self.request.route_path(
                'bucket_objects_count_versioning_json', name=self.bucket.name)
        )

    @view_config(route_name='bucket_details', renderer=VIEW_TEMPLATE)
    def bucket_details(self):
        return self.render_dict

    @view_config(route_name='bucket_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def bucket_update(self):
        if self.bucket and self.details_form.validate():
            location = self.request.route_path('bucket_details', name=self.bucket.name)
            with boto_error_handler(self.request, location):
                share_type = self.request.params.get('share_type')
                if share_type == 'public':
                    self.bucket.make_public(recursive=True)
                else:
                    self.set_sharing_acl(self.request, bucket_object=self.bucket, item_acl=self.bucket_acl)
                msg = '{0} {1}'.format(_(u'Successfully modified bucket'), self.bucket.name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.details_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='bucket_update_versioning', request_method='POST')
    def bucket_update_versioning(self):
        if self.bucket and self.versioning_form.validate():
            location = self.request.route_path('bucket_details', name=self.bucket.name)
            if self.request.params.get('source') == 'landingpage':
                location = self.request.route_path('buckets')
            with boto_error_handler(self.request, location):
                versioning_param = self.request.params.get('versioning_action')
                versioning_bool = True if versioning_param == 'enable' else False
                self.bucket.configure_versioning(versioning_bool)
                msg = '{0} {1}'.format(_(u'Successfully modified versioning status for bucket'), self.bucket.name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.versioning_form.get_errors_list()
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

    @staticmethod
    def set_sharing_acl(request, bucket_object=None, item_acl=None):
        sharing_grants_json = request.params.get('s3_sharing_acl')
        if sharing_grants_json:
            sharing_grants = json.loads(sharing_grants_json)
            grants = []
            for grant in sharing_grants:
                grants.append(Grant(
                    permission=grant.get('permission'),
                    id=grant.get('id'),
                    display_name=grant.get('display_name'),
                    type=grant.get('grant_type'),
                    uri=grant.get('uri'),
                ))
            sharing_acl = ACL()
            sharing_acl.grants = grants
            sharing_policy = Policy()
            sharing_policy.acl = sharing_acl
            sharing_policy.owner = item_acl.owner
            bucket_object.set_acl(sharing_policy)

    @staticmethod
    def get_bucket_creation_date(s3_conn, bucket_name):
        """Due to limitations in the AWS API, the creation date is missing when fetching a single bucket,
           so as a workaround we need to fetch all buckets and match the current one to get the creation timestamp.
           FIXME: Remove this hack if/when we have bucket.creation_date available via s3_conn.get_bucket()
        """
        buckets = s3_conn.get_all_buckets() if s3_conn else []
        matched_bucket = [bucket for bucket in buckets if bucket.name == bucket_name]
        if matched_bucket:
            return getattr(matched_bucket[0], 'creation_date', None)

    @staticmethod
    def get_bucket_owner_name(bucket_acl):
        if bucket_acl:
            owner_obj = bucket_acl.owner
            if owner_obj:
                return owner_obj.display_name

    @staticmethod
    def get_versioning_status(bucket):
        """Returns 'Disabled', 'Enabled', or 'Suspended'"""
        if bucket:
            status = bucket.get_versioning_status()
            return status.get('Versioning', 'Disabled')

    @staticmethod
    def get_versioning_update_action(versioning_status):
        """Returns 'enable' if status is Disabled or Suspended, otherwise returns 'disable'"""
        if versioning_status:
            return 'enable' if versioning_status in ['Disabled', 'Suspended'] else 'disable'


class BucketItemDetailsView(BaseView):
    """Views for Bucket item (folder/object) details"""
    VIEW_TEMPLATE = '../templates/buckets/bucket_item_details.pt'

    def __init__(self, request):
        super(BucketItemDetailsView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')
        with boto_error_handler(request):
            self.bucket = BucketContentsView.get_bucket(request, self.s3_conn)
            self.bucket_name = self.bucket.name
            self.bucket_item = self.get_bucket_item()
            self.bucket_item_acl = self.bucket_item.get_acl() if self.bucket_item else None
        if self.bucket_item is None:
            raise HTTPNotFound()
        unprefixed_name = BucketContentsView.get_unprefixed_key_name(self.bucket_item.name)
        self.friendly_name_param = self.request.params.get('friendly_name')
        self.name_updated = True if self.friendly_name_param and self.friendly_name_param != unprefixed_name else False
        self.bucket_item_name = self.bucket_item.name
        self.details_form = BucketItemDetailsForm(
            request, bucket_object=self.bucket_item, unprefixed_name=unprefixed_name,
            formdata=self.request.params or None
        )
        self.sharing_form = SharingPanelForm(
            request, bucket_object=self.bucket, sharing_acl=self.bucket_item_acl, formdata=self.request.params or None)
        self.versioning_form = BucketUpdateVersioningForm(request, formdata=self.request.params or None)
        self.metadata_form = MetadataForm(request, formdata=self.request.params or None)
        self.render_dict = dict(
            sharing_form=self.sharing_form,
            details_form=self.details_form,
            versioning_form=self.versioning_form,
            metadata_form=self.metadata_form,
            bucket=self.bucket,
            bucket_name=self.bucket.name,
            bucket_item=self.bucket_item,
            key_name=self.bucket_item.name,
            item_name=unprefixed_name,
            item_link=self.bucket_item.generate_url(expires_in=BUCKET_ITEM_URL_EXPIRES),
            item_download_url=BucketContentsView.get_item_download_url(self.bucket_item),
        )

    @view_config(route_name='bucket_item_details', renderer=VIEW_TEMPLATE)
    def bucket_item_details(self):
        return self.render_dict

    @view_config(route_name='bucket_item_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def bucket_item_update(self):
        if self.bucket and self.bucket_item and self.details_form.validate():
            # Set proper redirect location, handling an object name change when applicable
            location = self.request.route_path(
                'bucket_item_details',
                name=self.bucket.name,
                subpath='{0}/{1}'.format(
                    DELIMITER.join(self.request.subpath[:-1]),
                    self.friendly_name_param
                ) if self.name_updated else self.request.subpath
            )
            with boto_error_handler(self.request, location):
                # Update name
                self.update_name()
                # Update ACL
                self.update_acl()
                # Update metadata
                self.update_metadata()
                msg = '{0} {1}'.format(_(u'Successfully modified'), self.bucket_item.name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.details_form.get_errors_list()
        return self.render_dict

    def get_bucket_item(self):
        subpath = self.request.subpath
        item_key_name = DELIMITER.join(subpath)
        item = self.bucket.get_key(item_key_name)
        if item is None:  # Folder requires the trailing slash, which request.subpath omits
            item = self.bucket.get_key('{0}/'.format(item_key_name))
        return item

    def update_acl(self):
        share_type = self.request.params.get('share_type')
        if share_type == 'public':
            self.bucket.make_public()
        else:
            BucketDetailsView.set_sharing_acl(
                self.request, bucket_object=self.bucket_item, item_acl=self.bucket_item_acl)

    def update_metadata(self):
        """Update metadata and remove deleted metadata"""
        # Removed deleted metadata
        metadata_keys_to_delete_param = self.request.params.get('metadata_keys_to_delete') or '[]'
        metadata_keys_to_delete = json.loads(metadata_keys_to_delete_param)
        if metadata_keys_to_delete:
            for mkey in metadata_keys_to_delete:
                if self.bucket_item.get_metadata(mkey):
                    # Delete true metadata
                    del self.bucket_item.metadata[mkey]
                else:
                    # Delete removed header-like "metadata"
                    # NOTE: The 'Content-Type' header "metadata" cannot be fully removed,
                    #       as it will be set to 'binary/octet-stream' if removed and/or missing
                    normalized_mkey = mkey.replace('-', '_').lower()
                    if getattr(self.bucket_item, normalized_mkey, None):
                        delattr(self.bucket_item, normalized_mkey)
        # Update metadata
        metadata_param = self.request.params.get('metadata') or '{}'
        metadata = json.loads(metadata_param)
        metadata_attr_mapping = self.metadata_attribute_mapping()
        if metadata:
            for key, val in metadata.items():
                metadata_attribute = metadata_attr_mapping.get(key.lower())
                if metadata_attribute:
                    setattr(self.bucket_item, metadata_attribute, val)
                else:
                    self.bucket_item.set_metadata(key, val)

        if metadata or metadata_keys_to_delete:
            # The only way to update the metadata appears to be to copy the object
            copied_item = self.bucket_item.copy(
                self.bucket_name, self.bucket_item_name, metadata=self.bucket_item.metadata, preserve_acl=True)
            # Delete the old object if we performed a rename
            if self.name_updated:
                old_key = self.bucket_item.name
                self.bucket.delete_key(old_key)
            self.bucket_item = copied_item

    def update_name(self):
        friendly_name_param = self.request.params.get('friendly_name')
        key_name = self.bucket_item.name
        old_name = BucketContentsView.get_unprefixed_key_name(self.bucket_item.name)
        if friendly_name_param and friendly_name_param != old_name:
            new_name = '{0}/{1}'.format(
                DELIMITER.join(key_name.split(DELIMITER)[:-1]),
                friendly_name_param
            )
            self.bucket_item_name = new_name

    @staticmethod
    def attribute_metadata_mapping():
        """
        Map so-called "metadata" with their object attribute names
        :return: dict of attribute/header key/value pairs
        """
        return dict(
            content_disposition='Content-Disposition',
            content_type='Content-Type',
            content_language='Content-Language',
            content_encoding='Content-Encoding',
            cache_control='Cache-Control',
        )

    @classmethod
    def metadata_attribute_mapping(cls):
        """Converts metadata_attribute_mapping to be based on the header rather than the attribute name"""
        mapping = {}
        for key, val in cls.attribute_metadata_mapping().items():
            mapping[val] = key
        return mapping

    @classmethod
    def get_extended_metadata(cls, bucket_item):
        """Extend object metadata with metadata-like attributes"""
        metadata = bucket_item.metadata
        metadata_attr_mapping = cls.attribute_metadata_mapping()
        for attr in metadata_attr_mapping:
            if getattr(bucket_item, attr, None):
                metadata[metadata_attr_mapping[attr]] = getattr(bucket_item, attr)
        return metadata

