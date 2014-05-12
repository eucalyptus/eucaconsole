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
Core views

"""
import logging
import simplejson as json
import textwrap

from contextlib import contextmanager
from dateutil import tz
from urllib import urlencode
from urlparse import urlparse

from beaker.cache import cache_managers
from boto.ec2.blockdevicemapping import BlockDeviceType, BlockDeviceMapping
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPFound, HTTPException, HTTPUnprocessableEntity
from pyramid.i18n import TranslationString as _
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import notfound_view_config, view_config

from ..constants.images import AWS_IMAGE_OWNER_ALIAS_CHOICES, EUCA_IMAGE_OWNER_ALIAS_CHOICES
from ..forms.login import EucaLogoutForm
from ..models import Notification
from ..models.auth import ConnectionManager


class JSONResponse(Response):
    def __init__(self, status=200, message=None, **kwargs):
        super(JSONResponse, self).__init__(**kwargs)
        self.status = status
        self.content_type = 'application/json'
        self.body = json.dumps(
            dict(message=message)
        )


# Can use this for 1.5, but the fix below for 1.4 also works in 1.5.
#class JSONError(HTTPException):
class JSONError(HTTPUnprocessableEntity):
    def __init__(self, status=400, message=None, **kwargs):
        super(JSONError, self).__init__(**kwargs)
        self.status = status
        self.content_type = 'application/json'
        self.body = json.dumps(
            dict(message=message)
        )


class BaseView(object):
    """Base class for all views"""
    def __init__(self, request):
        self.request = request
        self.region = request.session.get('region')
        self.access_key = request.session.get('access_id')
        self.secret_key = request.session.get('secret_key')
        self.cloud_type = request.session.get('cloud_type')
        self.security_token = request.session.get('session_token')
        self.euca_logout_form = EucaLogoutForm(self.request)

    def get_connection(self, conn_type='ec2', cloud_type=None):
        conn = None
        if cloud_type is None:
            cloud_type = self.cloud_type

        if cloud_type == 'aws':
            conn = ConnectionManager.aws_connection(
                self.region, self.access_key, self.secret_key, self.security_token, conn_type)
        elif cloud_type == 'euca':
            host = self.request.registry.settings.get('clchost', 'localhost')
            port = int(self.request.registry.settings.get('clcport', 8773))
            if conn_type == 'ec2':
                host = self.request.registry.settings.get('ec2.host', host)
                port = self.request.registry.settings.get('ec2.port', port)
            elif conn_type == 'autoscale':
                host = self.request.registry.settings.get('autoscale.host', host)
                port = self.request.registry.settings.get('autoscale.port', port)
            elif conn_type == 'cloudwatch':
                host = self.request.registry.settings.get('cloudwatch.host', host)
                port = self.request.registry.settings.get('cloudwatch.port', port)
            elif conn_type == 'elb':
                host = self.request.registry.settings.get('elb.host', host)
                port = self.request.registry.settings.get('elb.port', port)
            elif conn_type == 'iam':
                host = self.request.registry.settings.get('iam.host', host)
                port = self.request.registry.settings.get('iam.port', port)
            elif conn_type == 'sts':
                host = self.request.registry.settings.get('sts.host', host)
                port = self.request.registry.settings.get('sts.port', port)

            conn = ConnectionManager.euca_connection(
                host, port, self.access_key, self.secret_key, self.security_token, conn_type)

        return conn

    def is_csrf_valid(self):
        return self.request.session.get_csrf_token() == self.request.params.get('csrf_token')

    def _store_file_(self, filename, mime_type, contents):
        session = self.request.session
        session['file_cache'] = (filename, mime_type, contents)

    def _has_file_(self):
        session = self.request.session
        return 'file_cache' in session

    @staticmethod
    def sanitize_url(url):
        default_path = '/'
        if not url:
            return default_path
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        if scheme:
            if not netloc:  # Prevent arbitrary redirects when url scheme has extra slash e.g. "http:///example.com"
                return default_path
            url = parsed_url.path
        return url or default_path

    @staticmethod
    def invalidate_connection_cache():
        """Empty connection objects cache"""
        for manager in cache_managers.values():
            namespace = manager.namespace.namespace
            if '_aws_connection' in namespace or '_euca_connection' in namespace:
                manager.clear()

    @staticmethod
    def log_message(request, message, level='info'):
        prefix = ''
        cloud_type = request.session.get('cloud_type', 'euca')
        if cloud_type == 'euca':
            account = request.session.get('account', '')
            username = request.session.get('username', '')
            prefix = '{0}/{1}'.format(account, username)
        elif cloud_type == 'aws':
            account = request.session.get('username_label', '')
            region = request.session.get('region')
            prefix = '{0}/{1}'.format(account, region)
        log_message = "{prefix} [{id}]: {msg}".format(prefix=prefix, id=request.id, msg=message)
        if level == 'info':
            logging.info(log_message)
        elif level == 'error':
            logging.error(log_message)

    def log_request(self, message):
        self.log_message(self.request, message)

    @staticmethod
    def handle_error(err=None, request=None, location=None, template="{0}"):
        status = getattr(err, 'status', None) or err.args[0] if err.args else ""
        message = template.format(err.reason)
        if err.error_message is not None:
            message = err.error_message
            if 'because of:' in message:
                message = message[message.index("because of:")+11:]
            if 'RelatesTo Error:' in message:
                message = message[message.index("RelatesTo Error:")+16:]
            # do we need this logic in the common code?? msg = err.message.split('remoteDevice')[0]
            # this logic found in volumes.js
        BaseView.log_message(request, message, level='error')
        if request.is_xhr:
            raise JSONError(message=message, status=status or 403)
        if status == 403:
            if any(['Invalid access key' in message, 'Invalid security token' in message]):
                notice = message
            else:
                notice = _(u'Your session has timed out. This may be due to inactivity, a policy that does not provide login permissions, or an unexpected error. Please log in again, and contact your cloud administrator if the problem persists.')
            request.session.flash(notice, queue=Notification.WARNING)
            # Empty Beaker cache to clear connection objects
            # BaseView.invalidate_connection_cache()
            raise HTTPFound(location=request.route_path('login'))
        request.session.flash(message, queue=Notification.ERROR)
        if location is None:
            location = request.current_route_url()
        raise HTTPFound(location)

    @staticmethod
    def escape_json(json_string):
        """Escape JSON strings passed to AngularJS controllers in templates"""
        replace_mapping = {
            "\'": "__apos__",
            '\\"': "__dquote__",
            "\\": "__bslash__",
        }
        for key, value in replace_mapping.items():
            json_string = json_string.replace(key, value)
        return json_string

    @staticmethod
    def dt_isoformat(dt_obj, tzone='UTC'):
        """Convert a timezone-unaware datetime object to tz-aware one and return it as an ISO-8601 formatted string"""
        return dt_obj.replace(tzinfo=tz.gettz(tzone)).isoformat()


class TaggedItemView(BaseView):
    """Common view for items that have tags (e.g. security group)"""

    def __init__(self, request):
        super(TaggedItemView, self).__init__(request)
        self.tagged_obj = None
        self.conn = None

    def add_tags(self):
        if self.conn:
            tags_json = self.request.params.get('tags')
            tags_dict = json.loads(tags_json) if tags_json else {}
            tags = {}
            for key, value in tags_dict.items():
                key = key.strip()
                if not any([key.startswith('aws:'), key.startswith('euca:')]):
                    tags[key] = value.strip()
            self.conn.create_tags([self.tagged_obj.id], tags)

    def remove_tags(self):
        if self.conn:
            tagkeys = []
            object_tags = self.tagged_obj.tags.keys()
            for tagkey in object_tags:
                if not any([tagkey.startswith('aws:'), tagkey.startswith('euca:')]):
                    tagkeys.append(tagkey)
            self.conn.delete_tags([self.tagged_obj.id], tagkeys)

    def update_tags(self):
        if self.tagged_obj is not None:
            self.remove_tags()
            self.add_tags()

    def update_name_tag(self, value):
        if self.tagged_obj is not None:
            if value != self.tagged_obj.tags.get('Name'):
                self.tagged_obj.remove_tag('Name')
                if value and not value.startswith('aws:'):
                    self.tagged_obj.add_tag('Name', value)

    @staticmethod
    def get_display_name(resource):
        name = ''
        if resource:
            name_tag = resource.tags.get('Name', '')
            name = '{0}{1}'.format(
                name_tag if name_tag else resource.id,
                ' ({0})'.format(resource.id) if name_tag else ''
            )
        return name

    @staticmethod
    def get_tags_display(tags, skip_name=True, wrap_width=0):
        """Return comma-separated list of tags as a string.
           Skips the 'Name' tag by default. no wrapping by default, otherwise honor wrap_width"""
        tags_array = []
        for key, val in tags.items():
            if not any([key.startswith('aws:'), key.startswith('euca:')]):
                template = '{0}={1}'
                if skip_name and key == 'Name':
                    continue
                else:
                    text = template.format(key, val)
                    if wrap_width > 0:
                        if len(text) > wrap_width:
                            tags_array.append(textwrap.fill(text, wrap_width))
                        else:
                            tags_array.append(text)
                    else:
                        tags_array.append(text)
        return ', '.join(tags_array)


class BlockDeviceMappingItemView(BaseView):
    def __init__(self, request):
        super(BlockDeviceMappingItemView, self).__init__(request)
        self.conn = self.get_connection()
        self.request = request

    def get_image(self):
        from eucaconsole.views.images import ImageView
        image_id = self.request.params.get('image_id')
        if self.conn and image_id:
            with boto_error_handler(self.request):
                image = self.conn.get_image(image_id)
                if image:
                    platform = ImageView.get_platform(image)
                    image.platform_name = ImageView.get_platform_name(platform)
                return image
        return None

    def get_owner_choices(self):
        if self.cloud_type == 'aws':
            return AWS_IMAGE_OWNER_ALIAS_CHOICES
        return EUCA_IMAGE_OWNER_ALIAS_CHOICES

    def get_snapshot_choices(self):
        choices = [('', _(u'None'))]
        for snapshot in self.conn.get_all_snapshots(owner='self'):
            value = snapshot.id
            snapshot_name = snapshot.tags.get('Name')
            label = '{id}{name} ({size} GB)'.format(
                id=snapshot.id,
                name=' - {0}'.format(snapshot_name) if snapshot_name else '',
                size=snapshot.volume_size
            )
            choices.append((value, label))
        return sorted(choices)

    def get_user_data(self):
        userdata_input = self.request.params.get('userdata')
        userdata_file_param = self.request.POST.get('userdata_file')
        userdata_file = userdata_file_param.file.read() if userdata_file_param else None
        userdata = userdata_file or userdata_input or None  # Look up file upload first
        return userdata

    @staticmethod
    def get_block_device_map(bdmapping_json=None):
        """Parse block_device_mapping JSON and return a configured BlockDeviceMapping object
        Mapping JSON structure...
            {"/dev/sda":
                {"snapshot_id": "snap-23E93E09", "volume_type": null, "delete_on_termination": true, "size": 1}  }
        """
        if bdmapping_json:
            mapping = json.loads(bdmapping_json)
            if mapping:
                bdm = BlockDeviceMapping()
                for key, val in mapping.items():
                    device = BlockDeviceType()
                    if val.get('volume_type') == 'ephemeral':
                        device.ephemeral_name = 'ephemeral0'
                    else:
                        device.volume_type = 'standard'
                        device.snapshot_id = val.get('snapshot_id') or None
                        device.size = val.get('size')
                        device.delete_on_termination = val.get('delete_on_termination', False)
                    bdm[key] = device
                return bdm
            return None
        return None


class LandingPageView(BaseView):
    """Common view for landing pages

    :ivar filter_keys: List of strings to pass to client-side filtering engine
        The search box input (usually above the landing page datagrid) will match each property in the list against
        each item in the collection to do the filtering.  See $scope.searchFilterItems in landingpage.js
    :ivar sort_keys: List of strings to pass to client-side sorting engine
        The sorting dropdown (usually above the landing page datagrid) will display a sorting option for
        each item in the list.  See templates/macros.pt (id="sorting_controls")
    :ivar initial_sort_key: The initial sort key used for Angular-based client-side sorting.
        Prefix the key with a '-' to perform a descending sort (e.g. '-launch_time')
    :ivar items: The list of dicts to pass to the JSON renderer to display the collection of items.
    :ivar prefix: The prefix for each landing page, relevant to the section
        For example, prefix = '/instances' for Instances

    """
    def __init__(self, request):
        super(LandingPageView, self).__init__(request)
        self.filter_fields = []
        self.filter_keys = []
        self.sort_keys = []
        self.initial_sort_key = ''
        self.items = []
        self.prefix = '/'

    def filter_items(self, items, ignore=None, autoscale=False):
        ignore = ignore or []  # Pass list of filters to ignore
        filtered_items = []
        if hasattr(self.request.params, 'dict_of_lists'):
            filter_params = self.request.params.dict_of_lists()
            for skip in ignore:
                if skip in filter_params.keys():
                    del filter_params[skip]
            if not filter_params:
                return items
            for item in items:
                matchedkey_count = 0
                for filter_key, filter_value in filter_params.items():
                    if filter_value and filter_value[0]:
                        if filter_key == 'tags':  # Special case to handle tags
                            if self.match_tags(item=item, tags=filter_value[0].split(','), autoscale=autoscale):
                                matchedkey_count += 1
                        elif hasattr(item, filter_key):
                            filterkey_val = getattr(item, filter_key, None)
                            if filterkey_val:
                                if isinstance(filterkey_val, list):
                                    for fitem in filterkey_val:
                                        if fitem in filter_value:
                                            matchedkey_count += 1
                                else:
                                    if filterkey_val in filter_value:
                                        matchedkey_count += 1
                    else:
                        matchedkey_count += 1  # Handle empty param values
                if matchedkey_count == len(filter_params):
                    filtered_items.append(item)
        return filtered_items

    @staticmethod
    def match_tags(item=None, tags=None, autoscale=False):
        for tag in tags:
            tag = tag.strip()
            if autoscale:  # autoscaling tags are a list of Tag boto.ec2.autoscale.tag.Tag objects
                if item.tags:
                    for as_tag in item.tags:
                        if as_tag and tag == as_tag.key or tag == as_tag.value:
                            return True
            else:  # Standard tags are a dict of key/value pairs
                if any([tag in item.tags.keys(), tag in item.tags.values()]):
                    return True
        return False

    def get_json_endpoint(self, route):
        return '{0}{1}'.format(
            self.request.route_path(route),
            '?{0}'.format(urlencode(self.request.params)) if self.request.params else ''
        )

    def get_redirect_location(self, route):
        location = '{0}'.format(self.request.route_path(route))
        if self.request.GET:
            location = '{0}?{1}'.format(location, urlencode(self.request.GET))
        return location


@notfound_view_config(renderer='../templates/notfound.pt')
def notfound_view(request):
    """404 Not Found view"""
    return dict()


@view_config(context=BotoServerError, permission=NO_PERMISSION_REQUIRED)
def conn_error(exc, request):
    """Generic handler for BotoServerError exceptions"""
    try:
        BaseView.handle_error(err=exc, request=request)
    except HTTPException as ex:
        return ex
    return


@contextmanager
def boto_error_handler(request, location=None, template="{0}"):
    try:
        yield
    except BotoServerError as err:
        BaseView.handle_error(err=err, request=request, location=location, template=template)


@view_config(route_name='file_download', request_method='POST')
def file_download(request):
    session = request.session
    if session.get('file_cache'):
        (filename, mime_type, contents) = session['file_cache']
        # Clean the session information regrading the new keypair
        del session['file_cache']
        response = Response(content_type=mime_type)
        response.body = str(contents)
        response.content_disposition = 'attachment; filename="{name}"'.format(name=filename)
        return response
    # this isn't handled on on client anyway, so we can return pretty much anything
    return Response(body='BaseView:file not found', status=500)

