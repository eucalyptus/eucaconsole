# -*- coding: utf-8 -*-
"""
Core views

"""
import simplejson as json
import textwrap
from urllib import urlencode

from beaker.cache import cache_managers
from boto.ec2.blockdevicemapping import BlockDeviceType, BlockDeviceMapping
from boto.exception import EC2ResponseError, BotoServerError

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.i18n import TranslationString as _
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import notfound_view_config, view_config

from ..constants.images import AWS_IMAGE_OWNER_ALIAS_CHOICES, EUCA_IMAGE_OWNER_ALIAS_CHOICES
from ..forms import GenerateFileForm
from ..forms.login import EucaLogoutForm
from ..models.auth import ConnectionManager


class JSONResponse(Response):
    def __init__(self, status=200, message=None, **kwargs):
        super(JSONResponse, self).__init__(**kwargs)
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
            host = self.request.registry.settings.get('clchost')
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
    def invalidate_cache():
        """Empty Beaker cache to clear connection objects"""
        for _cache in cache_managers.values():
            _cache.clear()

    @classmethod
    def handle_403_error(cls, exc, request=None):
        """Handle session timeout by redirecting to login page with notice.
           exc is usually a boto.exception.EC2ResponseError exception
        """
        status = getattr(exc, 'status', None) or exc.args[0] if exc.args else ""
        message = exc.message
        if request.is_xhr:
            return JSONResponse(status=status, message=message)
        if status in [403]:
            if any(['Invalid access key' in message, 'Invalid security token' in message]):
                notice = message
            else:
                notice = _(u'Your session has timed out')
            request.session.flash(notice, queue='warning')
            # Empty Beaker cache to clear connection objects
            cls.invalidate_cache()
            location = request.route_url('login')
            return HTTPFound(location=location)
        return HTTPForbidden()


class TaggedItemView(BaseView):
    """Common view for items that have tags (e.g. security group)"""

    def __init__(self, request):
        super(TaggedItemView, self).__init__(request)
        self.tagged_obj = None

    def add_tags(self):
        tags_json = self.request.params.get('tags')
        tags = json.loads(tags_json) if tags_json else {}

        for key, value in tags.items():
            if not key.strip().startswith('aws:'):
                self.tagged_obj.add_tag(key, value)

    def remove_tags(self):
        for tagkey, tagvalue in self.tagged_obj.tags.items():
            if not tagkey.startswith('aws:'):
                self.tagged_obj.remove_tag(tagkey, tagvalue)

    def update_tags(self):
        if self.tagged_obj is not None:
            self.remove_tags()
            self.add_tags()

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
            if not key.startswith('aws:'):
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

    def get_image(self):
        from eucaconsole.views.images import ImageView
        image_id = self.request.params.get('image_id')
        if self.conn and image_id:
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
        for snapshot in self.conn.get_all_snapshots():
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
                    device.volume_type = val.get('volume_type')  # 'EBS' or 'ephemeral'
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

    def filter_items(self, items, ignore=None):
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
                for fkey, fval in filter_params.items():
                    if fval and fval[0]:
                        if fkey == 'tags':  # Special case to handle tags
                            if self.match_tags(item=item, tags=fval[0].split(',')):
                                matchedkey_count += 1
                        elif hasattr(item, fkey) and getattr(item, fkey, None) in fval:
                            matchedkey_count += 1
                    else:
                        matchedkey_count += 1  # Handle empty param values
                if matchedkey_count == len(filter_params):
                    filtered_items.append(item)
        return filtered_items

    @staticmethod
    def match_tags(item=None, tags=None):
        for tag in tags:
            tag = tag.strip()
            if any([tag in item.tags.keys(), tag in item.tags.values()]):
                return True
        return False

    def get_json_endpoint(self, route):
        return '{0}{1}'.format(
            self.request.route_url(route),
            '?{0}'.format(urlencode(self.request.params)) if self.request.params else ''
        )

    def get_redirect_location(self, route):
        return '{0}'.format(self.request.route_url(route))


@notfound_view_config(renderer='../templates/notfound.pt')
def notfound_view(request):
    """404 Not Found view"""
    return dict()


@view_config(context=EC2ResponseError, permission=NO_PERMISSION_REQUIRED)
def ec2conn_error(exc, request):
    """Handle session timeout by redirecting to login page with notice."""
    return BaseView.handle_403_error(exc, request=request)


@view_config(context=BotoServerError, permission=NO_PERMISSION_REQUIRED)
def autoscale_error(exc, request):
    """Handle autoscale connection session timeout by redirecting to login page with notice."""
    return BaseView.handle_403_error(exc, request=request)

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

