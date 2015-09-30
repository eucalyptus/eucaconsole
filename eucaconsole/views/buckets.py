# -*- coding: utf-8 -*-
# Copyright 2013-2015 Hewlett Packard Enterprise Development LP
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
from datetime import datetime
import mimetypes
import simplejson as json
import urllib

from boto.exception import StorageCreateError
from boto.s3.acl import ACL, Grant, Policy
from boto.s3.bucket import Bucket
from boto.s3.key import Key
from boto.s3.prefix import Prefix
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPBadRequest
from pyramid.settings import asbool
from pyramid.view import view_config

from ..forms.buckets import (
    BucketDetailsForm, BucketItemDetailsForm, SharingPanelForm, BucketUpdateVersioningForm,
    MetadataForm, CreateBucketForm, CreateFolderForm, BucketDeleteForm, BucketUploadForm,
    BucketItemSharedURLForm)
from ..i18n import _
from ..models import Notification
from ..views import BaseView, LandingPageView, JSONResponse
from . import boto_error_handler
from .. import utils


DELIMITER = '/'
BUCKET_ITEM_URL_EXPIRES = 300  # Link to item expires in ___ seconds (after page load)
BUCKET_NAME_PATTERN = '^[a-z0-9-\.]+$'
FOLDER_NAME_PATTERN = '^[^\/]+$'
OBJECT_PATH_PATTERN = '^[a-z0-9-\.]+/.+$'


class BucketMixin(object):

    @staticmethod
    def real_path(request, bucket_name):
        if len(request.subpath) == 0:
            return ''
        path = request.environ['PATH_INFO'].decode('utf-8')
        if request.subpath[0] in bucket_name:
            path = path[path.index(bucket_name) + len(bucket_name):]
        path = path[path.index(request.subpath[0]):] if len(request.subpath) > 0 else ''
        return path

    def get_subpath(self, bucket_name):
        path = BucketMixin.real_path(self.request, bucket_name)
        subpath = []
        if path != '':
            if path.endswith('/'):  # and not path.endswith('//'):
                path = path[:-1]
            subpath = path.split('/')
        return tuple(subpath)


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
            dict(key='creation_date', name=_(u'Creation time: Oldest to Newest')),
            dict(key='-creation_date', name=_(u'Creation time: Newest to Oldest')),
        ]
        s3_conn = self.get_connection(conn_type='s3')
        s3_url_prefix = "https://{host}:{port}/{path}/".format(
            host=s3_conn.host,
            port=s3_conn.port,
            path=s3_conn.path
        )
        storage_key = self.get_shared_buckets_storage_key(s3_conn.host)
        self.render_dict = dict(
            prefix=self.prefix,
            versioning_form=BucketUpdateVersioningForm(request, formdata=self.request.params or None),
            delete_form=BucketDeleteForm(request),
            initial_sort_key='bucket_name',
            json_items_endpoint=self.get_json_endpoint('buckets_json'),
            sort_keys=self.sort_keys,
            filter_keys=['bucket_name'],
            controller_options_json=self.get_controller_options_json(storage_key),
            search_facets=BaseView.escape_json(json.dumps([])),
            bucket_name_pattern=BUCKET_NAME_PATTERN,
            object_path_pattern=OBJECT_PATH_PATTERN,
            object_url_prefix=s3_url_prefix,
            storage_key=storage_key
        )

    @view_config(route_name='buckets', renderer=VIEW_TEMPLATE)
    def buckets_landing(self):
        # sort_keys are passed to sorting drop-down
        return self.render_dict

    @view_config(route_name='bucket_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def bucket_delete(self):
        if self.is_csrf_valid():
            bucket_name = self.request.matchdict.get('name')
            s3_conn = self.get_connection(conn_type='s3')
            with boto_error_handler(self.request):
                self.log_request(u"Deleting bucket {0}".format(bucket_name))
                bucket = s3_conn.head_bucket(bucket_name)
                bucket.delete()
                msg = u'{0} {1}'.format(_(u'Successfully deleted bucket'), bucket_name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.request.route_path('buckets'))
        return self.render_dict

    def get_controller_options_json(self, storage_key):
        return BaseView.escape_json(json.dumps({
            'bucket_objects_count_url': self.request.route_path('bucket_objects_count_versioning_json', name='_name_'),
            'update_versioning_url': self.request.route_path('bucket_update_versioning', name='_name_'),
            'copy_object_url': self.request.route_path('bucket_put_item', name='_name_', subpath='_subpath_'),
            'get_keys_generic_url': self.request.route_path('bucket_keys', name='_name_', subpath='_subpath_'),
            'put_keys_url': self.request.route_path('bucket_put_items', name='_name_', subpath='_subpath_'),
            'upload_url': self.request.route_path('bucket_upload', name='_name_', subpath=''),
            'contents_url': self.request.route_path('bucket_contents', name='_name_', subpath=''),
            'bucket_item_url': self.request.route_path('bucket_item_url', name='_name_', subpath='_subpath_'),
            'storage_key': storage_key
        }))


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
                    contents_url=self.request.route_path('bucket_contents', name=bucket_name, subpath=''),
                    details_url=self.request.route_path('bucket_details', name=bucket_name),
                    creation_date=item.creation_date,
                ))
            return dict(results=buckets)

    @view_config(route_name='bucket_objects_count_versioning_json', renderer='json')
    def bucket_objects_count_versioning_json(self):
        with boto_error_handler(self.request):
            bucket = BucketContentsView.get_bucket(self.request, self.s3_conn) if self.s3_conn else []
            versioning_status = BucketDetailsView.get_versioning_status(bucket)
            versions = []
            if versioning_status != "Disabled":
                versions = bucket.get_all_versions()
        results = dict(
            object_count=len(tuple(bucket.list())),
            version_count=len(versions),
            versioning_status=versioning_status
        )
        return dict(results=results)

    def get_items(self):
        return self.s3_conn.get_all_buckets() if self.s3_conn else []


class BucketXHRView(BaseView, BucketMixin):
    """
    A view for bucket related XHR calls that carrys very little overhead
    """
    def __init__(self, request):
        super(BucketXHRView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')
        self.bucket_name = request.matchdict.get('name')
        request.subpath = self.get_subpath(self.bucket_name)

    @view_config(route_name='bucket_delete_keys', renderer='json', request_method='POST', xhr=True)
    def bucket_delete_keys(self):
        """
        Deletes keys from a bucket, attempting to do as many as possible, reporting errors back at the end.
        """
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        keys = self.request.params.get('keys')
        detailpage = self.request.params.get('detailpage')
        if not keys:
            return dict(message=_(u"keys must be specified."), errors=[])
        bucket = self.s3_conn.head_bucket(self.bucket_name)
        deleted_keys = ', '.join(keys) if isinstance(keys, list) else keys
        self.log_request(u"Deleting keys from {0} : {1}".format(self.bucket_name, deleted_keys))
        with boto_error_handler(self.request):
            result = bucket.delete_keys(keys.split(','))
            if result.errors:
                msg = _(u"Some key(s) couldn't be deleted. ") + \
                    ','.join([err.key + '(' + err.message + ')' for err in result.errors])
                if detailpage:
                    # Send notification via session on detail page since post-delete URL updates via window.location
                    self.request.session.flash(msg, queue=Notification.ERROR)
                return dict(errors=msg)
            else:
                msg = _(u"Successfully deleted key(s).")
                if detailpage:
                    # Send notification via session on detail page since post-delete URL updates via window.location
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                return dict(message=msg)

    @view_config(route_name='bucket_put_items', renderer='json', request_method='POST', xhr=True)
    def bucket_put_items(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        keys = self.request.params.get('keys')
        if not keys:
            return dict(message=_(u"keys must be specified."), errors=[])
        subpath = self.request.subpath
        src_bucket = self.request.params.get('src_bucket')
        folder_loc = self.request.params.get('folder_loc')
        with boto_error_handler(self.request):
            self.log_request(u"Copying key(s) from {0} to {1} : {2}".format(
                src_bucket, self.bucket_name + '/' + '/'.join(subpath), keys))
            bucket = self.s3_conn.get_bucket(self.bucket_name, validate=False)
            errors = []
            for k in keys.split(','):
                dest_key = '/'.join(subpath + (k[len(folder_loc):],))
                try:
                    bucket.copy_key(
                        new_key_name=dest_key,
                        src_bucket_name=src_bucket,
                        src_key_name=k
                    )
                except BotoServerError as err:
                    self.log_request("Couldn't copy " + k + ":" + err.message)
                    errors.append(k)
            if len(errors) == 0:
                return dict(message=_(u"Successfully copied object(s)."))
            else:
                return dict(message=_(u"Failed to copy all keys."), errors=errors)

    # TODO thinking this method can go away in favor of the other one above.
    @view_config(route_name='bucket_put_item', renderer='json', request_method='POST', xhr=True)
    def bucket_put_item(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        subpath = self.request.subpath
        src_bucket = self.request.params.get('src_bucket')
        src_key = self.request.params.get('src_key')
        dest_key = '/'.join(subpath) + '/' + src_key[src_key.rfind('/') + 1:]
        with boto_error_handler(self.request):
            self.log_request(u"Copying key from {0}:{1} to {2}:{3}".format(
                src_bucket, src_key, self.bucket_name, dest_key))
            bucket = self.s3_conn.get_bucket(self.bucket_name, validate=False)
            bucket.copy_key(
                new_key_name=dest_key,
                src_bucket_name=src_bucket,
                src_key_name=src_key
            )
            return dict(message=_(u"Successfully copied object."))

    @view_config(route_name='bucket_item_make_public', renderer='json', request_method='POST', xhr=True)
    def bucket_item_make_public(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        key_name = self.request.params.get('key')
        detailpage = self.request.params.get('detailpage')
        if not key_name:
            return dict(message=_(u"Key must be specified."), errors=[])
        bucket = self.s3_conn.head_bucket(self.bucket_name)
        key = bucket.get_key(key_name, validate=False)
        self.log_request(u"Making object {0} public".format(key_name))
        try:
            key.make_public()
            prefix = _(u"Successfully made object {0} public.")
            msg = prefix.format(key_name)
            if detailpage:
                # Need to send notification via session on detail page to allow ACLs to properly refresh
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return dict(message=msg)
        except BotoServerError as err:
            prefix = _(u"Failed to make object {0} public: {1}")
            message = prefix.format(key_name, err.message)
            self.log_request(message)
            return dict(message=message)


class BucketContentsView(LandingPageView, BucketMixin):
    """Views for actions on single bucket"""
    VIEW_TEMPLATE = '../templates/buckets/bucket_contents.pt'

    def __init__(self, request, bucket_name=None, **kwargs):
        super(BucketContentsView, self).__init__(request, **kwargs)
        self.s3_conn = self.get_connection(conn_type='s3')
        self.bucket_name = bucket_name or self.get_bucket_name(request)
        request.subpath = self.get_subpath(self.bucket_name)
        self.prefix = '/buckets'
        self.create_folder_form = CreateFolderForm(request, formdata=self.request.params or None)
        self.subpath = request.subpath
        self.key_prefix = '/'.join(self.subpath) if len(self.subpath) > 0 else ''
        self.file_uploads_enabled = asbool(self.request.registry.settings.get('file.uploads.enabled', True))
        self.render_dict = dict(
            bucket_name=self.bucket_name,
            versioning_form=BucketUpdateVersioningForm(request, formdata=self.request.params or None),
            delete_form=BucketDeleteForm(request),
            create_folder_form=self.create_folder_form,
        )

    @view_config(route_name='bucket_contents', renderer=VIEW_TEMPLATE)
    def bucket_contents(self):
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='-size', name=_(u'Size: Largest to smallest')),
            dict(key='size', name=_(u'Size: Smallest to largest')),
            dict(key='-last_modified', name=_(u'Modified time: Newest to Oldest')),
            dict(key='last_modified', name=_(u'Modified time: Oldest to Newest ')),
        ]
        # if shared bucket, we'd like to check permissions and send back to buckets page if none
        try:
            if self.s3_conn:
                self.s3_conn.get_bucket(self.bucket_name).list(prefix='notlikely')
        except BotoServerError as err:
            # 404: not found
            if err.status == 404:
                msg = _(u'Bucket does not exist')
            # 403: forbidden
            if err.status == 403:
                msg = _(
                    u'You do not have the required permissions to perform this operation. '
                    u'Please contact your cloud administrator to request an updated access policy.'
                )
            self.request.session.flash(msg, queue=Notification.ERROR)
            return HTTPFound(location=self.request.route_path('buckets'))
        json_route_path = self.request.route_path('bucket_contents', name=self.bucket_name, subpath=self.subpath)
        if len(self.subpath) > 0 and self.subpath[-1] == '':
            json_route_path += '/'
        self.render_dict.update(
            prefix=self.prefix,
            key_prefix=self.key_prefix,
            display_path=self.key_prefix or self.bucket_name,
            initial_sort_key='name',
            json_items_endpoint=u"{0}?{1}".format(json_route_path, self.key_prefix),
            sort_keys=self.sort_keys,
            filter_keys=['name'],
            search_facets=BaseView.escape_json(json.dumps([])),
            controller_options_json=self.get_controller_options_json(),
        )
        return self.render_dict

    @view_config(route_name='bucket_upload', renderer='../templates/buckets/bucket_upload.pt', request_method='GET')
    def bucket_upload(self):
        if not self.file_uploads_enabled:
            raise HTTPNotFound()  # Return 404 if file uploads are disabled
        with boto_error_handler(self.request):
            metadata_form = MetadataForm(self.request, formdata=self.request.params or None)
            if self.bucket_name != '__shared__':
                bucket = BucketContentsView.get_bucket(self.request, self.s3_conn)
                if not hasattr(bucket, 'metadata'):
                    bucket.metadata = {}
                acl_obj = Key(bucket, '')
                sharing_form = SharingPanelForm(
                    self.request, bucket_object=acl_obj, sharing_acl=None, formdata=self.request.params or None)
                self.render_dict.update(
                    bucket=bucket,
                    bucket_name=bucket.name,
                    acl_obj=acl_obj,
                    upload_form=BucketUploadForm(self.request),
                    sharing_form=sharing_form,
                    metadata_form=metadata_form,
                )
            else:
                acl_obj = None
                sharing_form = SharingPanelForm(
                    self.request, bucket_object=acl_obj, sharing_acl=None, formdata=self.request.params or None)
                self.render_dict.update(
                    bucket=None,
                    bucket_name=self.bucket_name,
                    upload_form=BucketUploadForm(self.request),
                    acl_obj=acl_obj,
                    sharing_form=sharing_form,
                    metadata_form=metadata_form,
                    object_path_pattern=OBJECT_PATH_PATTERN,
                )
        return self.render_dict

    @view_config(route_name='bucket_upload', renderer='json', request_method='POST', xhr=True)
    def bucket_upload_post(self):
        if not self.file_uploads_enabled:
            raise HTTPBadRequest()  # Return 400 if file uploads are disabled
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        bucket_name = self.request.matchdict.get('name')
        shared_object_path = self.request.params.get('shared-object-path')
        folder = None
        if shared_object_path is not None:
            if shared_object_path.find('/') == -1:
                bucket_name = shared_object_path
                folder = ''
            else:
                bucket_name = shared_object_path[:shared_object_path.find('/')]
                folder = shared_object_path[shared_object_path.find('/') + 1:]
        files = self.request.POST.getall('files')
        with boto_error_handler(self.request):
            bucket = self.s3_conn.get_bucket(bucket_name, validate=False)
            for upload_file in files:
                upload_file.file.seek(0, 2)  # seek to end
                if upload_file.file.tell() > 5000000000:
                    return JSONResponse(status=400, message=_(u"File too large :") + upload_file.filename)
                upload_file.file.seek(0, 0)  # seek to start
                if folder:
                    if folder == '':
                        the_key = upload_file.filename
                    else:
                        the_key = "{0}/{1}".format(folder, upload_file.filename)
                else:
                    the_key = "/".join(self.request.subpath)
                bucket_item = bucket.new_key(the_key)
                self.log_request(u"Uploading file {0} to bucket {1}".format(bucket_item.key, bucket_name))
                bucket_item.set_metadata('Content-Type', upload_file.type)
                headers = {'Content-Type': upload_file.type}
                bucket_item.set_contents_from_file(fp=upload_file.file, headers=headers, replace=True)
                BucketDetailsView.update_acl(self.request, bucket_object=bucket_item)
                metadata_param = self.request.params.get('metadata') or '{}'
                metadata = json.loads(metadata_param)
                metadata_attr_mapping = BucketItemDetailsView.metadata_attribute_mapping()
                if metadata:
                    for key, val in metadata.items():
                        metadata_attribute = metadata_attr_mapping.get(key.lower())
                        if metadata_attribute:
                            setattr(bucket_item, metadata_attribute, val)
                        else:
                            bucket_item.set_metadata(key, val)
                    # The only way to update the metadata appears to be to copy the object
                    bucket_item.copy(
                        bucket_name, bucket_item.name, metadata=bucket_item.metadata, preserve_acl=True)

            return dict(results=True)

    @view_config(route_name='bucket_sign_req', renderer='json', request_method='POST', xhr=True)
    def bucket_sign_req(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        access = self.request.session['access_id']
        secret = self.request.session['secret_key']
        token = self.request.session['session_token']
        policy = BaseView.generate_default_policy(self.bucket_name, self.subpath, token)
        policy_signature = BaseView.gen_policy_signature(policy, secret)

        url = u"http://{host}:{port}/{path}/{bucket_name}".format(
            host=self.s3_conn.host, port=str(self.s3_conn.port),
            path=self.s3_conn.path, bucket_name=self.bucket_name
        )
        url = url.replace('///', '/')
        fields = {
            'key': self.subpath,
            'acl': 'ec2-bundle-read',
            'AWSAccessKeyId': access,
            'Policy': policy,
            'x-amz-security-token': token,
            'Signature': policy_signature
        }

        return dict(results=dict(url=url, fields=fields))

    @view_config(route_name='bucket_create_folder', request_method='POST')
    def bucket_create_folder(self):
        folder_name = self.request.params.get('folder_name')
        if folder_name and self.create_folder_form.validate():
            folder_name = folder_name.replace('/', '_')
            subpath = self.request.subpath
            prefix = DELIMITER.join(subpath)
            new_folder_key = u'{0}/{1}/'.format(prefix, folder_name)
            location = self.request.route_path('bucket_contents', name=self.bucket_name, subpath=subpath)
            with boto_error_handler(self.request):
                self.log_request(u"Creating folder {0} in bucket {1}".format(new_folder_key, self.bucket_name,))
                bucket = self.get_bucket(self.request, self.s3_conn, bucket_name=self.bucket_name)
                new_folder = bucket.new_key(new_folder_key)
                new_folder.set_contents_from_string('')
                msg = u'{0} {1}'.format(_(u'Successfully added folder'), folder_name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_folder_form.get_errors_list()
        return self.render_dict

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'bucket_name': self.bucket_name,
            'delete_keys_url': self.request.route_path('bucket_delete_keys', name=self.bucket_name),
            'get_keys_url': self.request.route_path('bucket_keys', name=self.bucket_name, subpath=self.request.subpath),
            'key_prefix': self.key_prefix,
            'copy_object_url': self.request.route_path('bucket_put_item', name='_name_', subpath='_subpath_'),
            'get_keys_generic_url': self.request.route_path('bucket_keys', name='_name_', subpath='_subpath_'),
            'put_keys_url': self.request.route_path('bucket_put_items', name=self.bucket_name, subpath='_subpath_'),
            'make_object_public_url': self.request.route_path(
                'bucket_item_make_public', name=self.bucket_name, subpath='_subpath_'),
        }))

    @staticmethod
    def get_bucket_name(request):
        return request.matchdict.get('name')

    @staticmethod
    def get_unprefixed_key_name(key_name):
        """Returns key name without the prefix (i.e. without the folder path)"""
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
        bucket_name = bucket_name or request.matchdict.get('name')
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
            response_headers={u'response-content-disposition': 'attachment; filename={0}'.format(item_name)},
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


class BucketContentsJsonView(BaseView, BucketMixin):
    def __init__(self, request, bucket=None, **kwargs):
        super(BucketContentsJsonView, self).__init__(request, **kwargs)
        self.bucket = bucket
        with boto_error_handler(request):
            self.s3_conn = self.get_connection(conn_type='s3')
            if self.s3_conn and self.bucket is None:
                self.bucket = BucketContentsView.get_bucket(request, self.s3_conn)
        self.bucket_name = self.bucket.name
        request.subpath = self.get_subpath(self.bucket_name)
        self.subpath = request.subpath

    @view_config(route_name='bucket_contents', renderer='json', request_method='POST', xhr=True)
    def bucket_contents_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        items = []
        list_prefix = u'{0}/'.format(DELIMITER.join(self.subpath)) if self.subpath else ''
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
                full_key_name=key.name,
                absolute_path=self.get_absolute_path(key.name),
                details_url=self.request.route_path('bucket_item_details', name=self.bucket.name, subpath=key.name),
            ))
            items.append(item)
        return dict(results=items)

    @view_config(route_name='bucket_keys', renderer='json', request_method='POST', xhr=True)
    def bucket_keys_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        items = []
        list_prefix = u'{0}/'.format(DELIMITER.join(self.subpath)) if len(self.subpath) > 0 else ''
        params = dict()
        if list_prefix:
            params.update(dict(prefix=list_prefix))
        bucket_items = self.bucket.list(**params)

        for key in bucket_items:
            items.append(key.name)
        return dict(results=items)

    def get_absolute_path(self, key_name):
        key_name = urllib.quote(key_name.encode('utf-8'), '')
        # NOTE: Need to hard-code the path here due to escaped key name
        return u'/buckets/{0}/contents/{1}'.format(self.bucket_name, key_name)

    def skip_item(self, key):
        """Skip item if it contains a folder path that doesn't match the current request subpath"""
        # Test if request subpath matches current folder
        if DELIMITER in key.name:
            joined_subpath = DELIMITER.join(self.subpath)
            if key.name == u'{0}{1}'.format(joined_subpath, DELIMITER):
                return True
            else:
                return False
        return False


class BucketDetailsView(BaseView, BucketMixin):
    """Views for Bucket details"""
    VIEW_TEMPLATE = '../templates/buckets/bucket_details.pt'

    def __init__(self, request, bucket=None, bucket_acl=None, **kwargs):
        super(BucketDetailsView, self).__init__(request, **kwargs)
        self.s3_conn = self.get_connection(conn_type='s3')
        self.bucket = bucket
        self.bucket_acl = bucket_acl
        with boto_error_handler(request):
            if self.s3_conn and self.bucket is None:
                self.bucket = BucketContentsView.get_bucket(request, self.s3_conn)
            request.subpath = self.get_subpath(self.bucket.name) if self.bucket else ''
            if self.bucket and self.bucket_acl is None:
                self.bucket_acl = self.bucket.get_acl() if self.bucket else None
        self.details_form = BucketDetailsForm(request, formdata=self.request.params or None)
        self.sharing_form = SharingPanelForm(
            request, bucket_object=self.bucket, sharing_acl=self.bucket_acl, formdata=self.request.params or None)
        self.versioning_form = BucketUpdateVersioningForm(request, formdata=self.request.params or None)
        self.create_folder_form = CreateFolderForm(request, formdata=self.request.params or None)
        self.versioning_status = self.get_versioning_status(self.bucket)
        if self.bucket is None:
            self.render_dict = dict()
        else:
            self.render_dict = dict(
                details_form=self.details_form,
                sharing_form=self.sharing_form,
                versioning_form=self.versioning_form,
                create_folder_form=self.create_folder_form,
                delete_form=BucketDeleteForm(request),
                bucket=self.bucket,
                bucket_creation_date=self.get_bucket_creation_date(self.s3_conn, self.bucket.name),
                bucket_name=self.bucket.name,
                owner=self.get_bucket_owner_name(self.bucket_acl),
                versioning_status=self.versioning_status,
                update_versioning_action=self.get_versioning_update_action(self.versioning_status),
                logging_status=self.get_logging_status(),
                bucket_contents_url=self.request.route_path('bucket_contents', name=self.bucket.name, subpath=''),
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
                self.log_request(u"Modifying bucket {0} acl".format(self.bucket.name))
                self.update_acl(self.request, bucket_object=self.bucket)
                msg = u'{0} {1}'.format(_(u'Successfully modified bucket'), self.bucket.name)
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
                self.log_request(u"Modifying bucket {0} versioning status {1}".format(
                    self.bucket.name, versioning_param))
                versioning_bool = True if versioning_param == 'enable' else False
                self.bucket.configure_versioning(versioning_bool)
                msg = u'{0} {1}'.format(_(u'Successfully modified versioning status for bucket'), self.bucket.name)
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
                logging_prefix = u'{0}/'.format(logging_prefix.split(DELIMITER)[0])
            logging_subpath = u'{0}/{1}'.format(self.bucket.name, logging_prefix)
            return dict(
                enabled=logging_enabled,
                logs_prefix=logging_prefix,
                logs_url=self.request.route_path('bucket_contents', name=self.bucket.name, subpath=logging_subpath)
            )

    @staticmethod
    def update_acl(request, bucket_object=None):
        is_bucket = isinstance(bucket_object, Bucket)
        propagate_acls = request.params.get('propagate_acls') == 'y'
        # Save manually entered ACLs
        sharing_acl = BucketDetailsView.get_sharing_acl(
            request, bucket_object=bucket_object, item_acl=bucket_object.get_acl())
        if sharing_acl:
            bucket_object.set_acl(sharing_acl)
            if is_bucket and propagate_acls:
                bucket_keys = bucket_object.get_all_keys()
                # Set manual ACL recursively
                for key in bucket_keys:
                    key.set_acl(sharing_acl)

    @staticmethod
    def get_sharing_acl(request, bucket_object=None, item_acl=None):
        sharing_grants_json = request.params.get('s3_sharing_acl', '[]')
        sharing_grants = json.loads(sharing_grants_json)
        sharing_policy = None
        if sharing_grants:
            sharing_acl = ACL()
            for grant in sharing_grants:
                email_address = grant.get('email_address')
                permission = grant.get('permission')
                if email_address:
                    sharing_acl.add_email_grant(permission, email_address)
                else:
                    sharing_acl.add_grant(Grant(
                        permission=permission,
                        id=grant.get('id') or None,
                        display_name=grant.get('display_name') or None,
                        type=grant.get('grant_type'),
                        uri=grant.get('uri'),
                    ))
            sharing_policy = Policy()
            sharing_policy.acl = sharing_acl
            sharing_policy.owner = item_acl.owner if item_acl else bucket_object.get_acl().owner
        return sharing_policy

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


class BucketItemDetailsView(BaseView, BucketMixin):
    """Views for Bucket item (folder/object) details"""
    VIEW_TEMPLATE = '../templates/buckets/bucket_item_details.pt'

    def __init__(self, request, bucket=None, bucket_item_acl=None, **kwargs):
        super(BucketItemDetailsView, self).__init__(request, **kwargs)
        self.bucket = bucket
        self.bucket_item_acl = bucket_item_acl
        self.s3_conn = self.get_connection(conn_type='s3')
        with boto_error_handler(request):
            if self.s3_conn and self.bucket is None:
                self.bucket = BucketContentsView.get_bucket(request, self.s3_conn)
                self.s3_conn.suppress_consec_slashes = False
            request.subpath = self.get_subpath(self.bucket.name)
            self.bucket_name = self.bucket.name
            self.bucket_item = self.get_bucket_item()
            if self.s3_conn and self.bucket_item_acl is None:
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
            request, bucket_object=self.bucket_item, sharing_acl=self.bucket_item_acl,
            formdata=self.request.params or None)
        self.versioning_form = BucketUpdateVersioningForm(request, formdata=self.request.params or None)
        self.metadata_form = MetadataForm(request, formdata=self.request.params or None)
        self.shared_url_form = BucketItemSharedURLForm(request, formdata=self.request.params or None)
        self.render_dict = dict(
            sharing_form=self.sharing_form,
            details_form=self.details_form,
            versioning_form=self.versioning_form,
            metadata_form=self.metadata_form,
            shared_url_form=self.shared_url_form,
            bucket=self.bucket,
            bucket_name=self.bucket.name,
            bucket_item=self.bucket_item,
            last_modified=self.get_last_modified_time(self.bucket_item),
            key_name=self.bucket_item.name,
            item_name=unprefixed_name,
            item_link=self.get_unsigned_url(),
            item_is_public=self.get_public_status(grants=self.bucket_item_acl.acl.grants),
            item_open_url=self.bucket_item.generate_url(expires_in=BUCKET_ITEM_URL_EXPIRES),
            item_download_url=BucketContentsView.get_item_download_url(self.bucket_item),
            cancel_link_url=self.get_cancel_link_url(),
            ufshost_error=utils.is_ufshost_error(self.s3_conn, self.cloud_type)
        )

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'delete_keys_url': self.request.route_path('bucket_delete_keys', name=self.bucket_name),
            'bucket_url': self.request.route_path(
                'bucket_contents', name=self.bucket_name, subpath=self.request.subpath[:-1]),
            'make_object_public_url': self.request.route_path(
                'bucket_item_make_public', name=self.bucket_name, subpath='_subpath_'),
            'bucket_item_generate_url_endpoint': self.request.route_path(
                'bucket_item_generate_url', name=self.bucket_name, subpath=self.request.subpath),
            'bucket_item_key': self.bucket_item_name,
            'unprefixed_key': BucketContentsView.get_unprefixed_key_name(self.bucket_item.name)
        }))

    @view_config(route_name='bucket_item_details', renderer=VIEW_TEMPLATE)
    def bucket_item_details(self):
        self.render_dict.update(dict(controller_options_json=self.get_controller_options_json()))
        return self.render_dict

    @view_config(route_name='bucket_item_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def bucket_item_update(self):
        if self.bucket and self.bucket_item and self.details_form.validate():
            # Set proper redirect location, handling an object name change when applicable
            location = self.request.route_path(
                'bucket_item_details',
                name=self.bucket.name,
                subpath=u'{0}/{1}'.format(
                    DELIMITER.join(self.request.subpath[:-1]),
                    self.friendly_name_param
                ) if self.name_updated else self.request.subpath
            )
            with boto_error_handler(self.request, location):
                self.log_request(u"Modifying item {0} in bucket {1}".format(self.bucket_item.name, self.bucket.name))
                # Update name
                self.update_name()
                # Update ACL
                BucketDetailsView.update_acl(self.request, bucket_object=self.bucket_item)
                # Update metadata
                self.update_metadata()
                msg = u'{0} {1}'.format(_(u'Successfully modified'), self.bucket_item.name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.details_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='bucket_item_generate_url', renderer='json', request_method='POST')
    def bucket_item_generate_url(self):
        item = self.get_bucket_item()
        expiration = int(self.request.params.get('expiration', 3600))
        return dict(
            shared_link=item.generate_url(expires_in=expiration)
        )

    def get_bucket_item(self):
        subpath = self.request.subpath
        item_key_name = DELIMITER.join(subpath)
        item = self.bucket.get_key(item_key_name)
        if item is None:  # Folder requires the trailing slash, which request.subpath omits
            item = self.bucket.get_key(u'{0}/'.format(item_key_name))
        return item

    def get_unsigned_url(self):
        """Returns unsigned URL for object with query string removed"""
        item_url = self.bucket_item.generate_url(expires_in=0, query_auth=False)
        return item_url.split('?')[0]

    @staticmethod
    def get_public_status(grants=None):
        """Determine whether an object is public based on its ACL grants
        :type grants: list
        :param grants: List of boto.s3.acl.Grant objects
        :returns: True if object is public, else False
        :rtype: bool

        """
        all_users_uri = 'http://acs.amazonaws.com/groups/global/AllUsers'
        grants = grants or []
        for grant in grants:
            if grant.uri and grant.uri == all_users_uri:
                return True
        return False

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
            new_name = u'{0}/{1}'.format(
                DELIMITER.join(key_name.split(DELIMITER)[:-1]),
                friendly_name_param
            )
            self.bucket_item_name = new_name

    def get_cancel_link_url(self):
        subpath = DELIMITER.join(self.request.subpath[:-1])
        return self.request.route_path('bucket_contents', name=self.bucket_name, subpath=subpath)

    @staticmethod
    def get_last_modified_time(bucket_object):
        """
        :returns an ISO-8601 formatted timestamp of an object's last-modified date/time
        :rtype str or None
        """
        if bucket_object and bucket_object.last_modified:
            parsed_time = datetime.strptime(bucket_object.last_modified, '%a, %d %b %Y %H:%M:%S %Z')
            return u'{0}Z'.format(parsed_time.isoformat())
        return None

    @staticmethod
    def attribute_metadata_mapping():
        """
        Map header "metadata" with their object attribute names
        :return: dict of attribute/header key/value pairs
        """
        return dict(
            content_disposition='Content-Disposition',
            content_type='Content-Type',
            content_language='Content-Language',
            content_encoding='Content-Encoding',
            cache_control='Cache-Control',
        )

    @staticmethod
    def metadata_attribute_mapping():
        """Converts metadata_attribute_mapping to be based on the header rather than the attribute name"""
        mapping = {}
        for key, val in BucketItemDetailsView.attribute_metadata_mapping().items():
            mapping[val] = key
        return mapping

    @classmethod
    def get_extended_metadata(cls, bucket_item):
        """Extend object metadata with metadata-like attributes"""
        metadata = bucket_item.metadata if bucket_item else {}
        metadata_attr_mapping = cls.attribute_metadata_mapping()
        for attr in metadata_attr_mapping:
            if getattr(bucket_item, attr, None):
                metadata[metadata_attr_mapping[attr]] = getattr(bucket_item, attr)
        return metadata


class BucketSharedItemView(BaseView, BucketMixin):
    def __init__(self, request, bucket=None, bucket_item_acl=None, **kwargs):
        super(BucketSharedItemView, self).__init__(request, **kwargs)
        self.bucket = bucket
        s3_conn = self.get_connection(conn_type='s3')
        request.subpath = self.get_subpath(self.bucket.name)
        if s3_conn and self.bucket is None:
            bucket_name = request.matchdict.get('name')
            self.bucket = s3_conn.get_bucket(bucket_name, validate=False)
            self.bucket_item = self.bucket.get_key('/'.join(request.subpath), validate=False)

    @view_config(route_name='bucket_item_url', renderer='json', request_method='POST', xhr=True)
    def bucket_item_url(self):
        return dict(
            item_link=BucketContentsView.get_item_download_url(self.bucket_item),
        )


class CreateBucketView(BaseView):
    """Views for creating a bucket"""
    VIEW_TEMPLATE = '../templates/buckets/bucket_new.pt'

    def __init__(self, request):
        super(CreateBucketView, self).__init__(request)
        with boto_error_handler(request):
            self.s3_conn = self.get_connection(conn_type='s3')
        self.create_form = CreateBucketForm(request, formdata=self.request.params or None)
        self.sharing_form = SharingPanelForm(request, formdata=self.request.params or None)
        self.render_dict = dict(
            create_form=self.create_form,
            sharing_form=self.sharing_form,
            bucket_name_pattern=BUCKET_NAME_PATTERN,
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='bucket_new', renderer=VIEW_TEMPLATE)
    def bucket_new(self):
        return self.render_dict

    @view_config(route_name='bucket_create', renderer=VIEW_TEMPLATE, request_method='POST')
    def bucket_create(self):
        if self.create_form.validate():
            bucket_name = self.request.params.get('bucket_name')
            bucket_name = bucket_name.strip().lower()
            enable_versioning = self.request.params.get('enable_versioning') == 'y'
            location = self.request.route_path('bucket_details', name=bucket_name)
            with boto_error_handler(self.request, self.request.route_path('buckets')):
                self.log_request(u"Creating bucket {0}".format(bucket_name))
                try:
                    new_bucket = self.s3_conn.create_bucket(bucket_name)
                    BucketDetailsView.update_acl(self.request, bucket_object=new_bucket)
                    if enable_versioning:
                        new_bucket.configure_versioning(True)
                    msg = u'{0} {1}'.format(_(u'Successfully created'), bucket_name)
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                except StorageCreateError as err:
                    # Handle bucket name conflict
                    self.request.error_messages = [err.message]
                    return self.render_dict
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
        return self.render_dict

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'bucket_name': self.request.params.get('bucket_name', ''),
            'share_type': self.request.params.get('share_type', 'public'),
            'existing_bucket_names': self.get_existing_bucket_names(),
        }))

    def get_existing_bucket_names(self):
        return [bucket.name for bucket in self.s3_conn.get_all_buckets()]


class CreateBucketXHRView(BaseView):
    """Views for creating a bucket via XHR from non-bucket pages (e.g. ELB detail page)"""

    def __init__(self, request):
        super(CreateBucketXHRView, self).__init__(request)
        with boto_error_handler(request):
            self.s3_conn = self.get_connection(conn_type='s3')
        self.create_form = CreateBucketForm(request, formdata=self.request.params or None)

    @view_config(route_name='bucket_create_xhr', renderer='json', request_method='POST')
    def bucket_create_xhr(self):
        if self.create_form.validate():
            bucket_name = self.request.params.get('bucket_name').lower()
            if bucket_name in [bucket.name for bucket in self.s3_conn.get_all_buckets()]:
                conflict_message = _(
                    u'The bucket name you have entered conflicts with an existing bucket in your account. '
                    u'Please use a different name.')
                return JSONResponse(status=409, message=conflict_message)
            self.log_request(u"Creating bucket {0}".format(bucket_name))
            try:
                self.s3_conn.create_bucket(bucket_name)
                msg = u'{0} {1}'.format(_(u'Successfully created'), bucket_name)
                return JSONResponse(message=msg)
            except StorageCreateError as err:
                # Handle bucket name conflict
                return JSONResponse(status=409, message=err.message)
        else:
            error_messages = ', '.join(self.create_form.get_errors_list())
            return JSONResponse(status=400, message=error_messages)
