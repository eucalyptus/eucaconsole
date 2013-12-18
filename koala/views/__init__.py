# -*- coding: utf-8 -*-
"""
Core views

"""
import simplejson as json
from urllib import urlencode

from beaker.cache import cache_managers
from boto.exception import EC2ResponseError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import notfound_view_config, view_config

from ..models.auth import ConnectionManager


class BaseView(object):
    """Base class for all views"""
    def __init__(self, request):
        self.request = request
        self.region = request.session.get('region')
        self.access_key = request.session.get('access_id')
        self.secret_key = request.session.get('secret_key')
        self.cloud_type = request.session.get('cloud_type')
        self.clchost = request.registry.settings.get('clchost') if request.registry.settings else 'localhost'
        self.clcport = int(request.registry.settings.get('clcport', 8773)) if request.registry.settings else 8773
        self.security_token = request.session.get('session_token')

    def get_connection(self, conn_type='ec2'):
        conn = None

        if self.cloud_type == 'aws':
            conn = ConnectionManager.aws_connection(
                self.region, self.access_key, self.secret_key, self.security_token, conn_type)
        elif self.cloud_type == 'euca':
            conn = ConnectionManager.euca_connection(
                self.clchost, self.clcport, self.access_key, self.secret_key, self.security_token, conn_type)

        return conn

    @staticmethod
    def invalidate_cache():
        """Empty Beaker cache to clear connection objects"""
        for _cache in cache_managers.values():
            _cache.clear()


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
    def get_tags_display(tags, skip_name=True):
        """Return comma-separated list of tags as a string.
           Skips the 'Name' tag by default"""
        if skip_name:
            tags_array = ['{0}={1}'.format(key, val) for key, val in tags.items() if key != 'Name']
        else:
            tags_array = ['{0}={1}'.format(key, val) for key, val in tags.items()]
        return ', '.join(tags_array)


class LandingPageView(BaseView):
    """Common view for landing pages

    :ivar display_type: Either 'tableview' or 'gridview'.  Defaults to 'gridview' if unspecified
    :ivar filter_fields: List of models.LandingPageFilter instances for landing page filters (usually at left)
        Leave empty to hide filters on landing page
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
        self.display_type = self.request.params.get('display', 'gridview')
        self.filter_fields = []
        self.filter_keys = []
        self.sort_keys = []
        self.initial_sort_key = ''
        self.items = []
        self.prefix = '/'

    def filter_items(self, items):
        """Filter items based on filter fields form"""
        ignored_filters = ['filter', 'display']
        filtered_params = [param for param in self.request.params.keys() if param not in ignored_filters]
        if not filtered_params:
            return items
        filtered_items = []
        filters = []
        for filter_field in self.filter_fields:
            value = self.request.params.get(filter_field.key)
            if value:
                filters.append((filter_field.key, value))
        for item in items:
            matchedkey_count = 0
            for fkey, fval in filters:
                if fval and hasattr(item, fkey) and getattr(item, fkey, None) == fval:
                    matchedkey_count += 1
            # Add to filtered items if *all* conditions match
            if matchedkey_count == len(filters):
                filtered_items.append(item)
        return filtered_items

    def get_json_endpoint(self, route):
        return '{0}{1}'.format(
            self.request.route_url(route),
            '?{0}'.format(urlencode(self.request.params)) if self.request.params else ''
        )

    def get_redirect_location(self, route):
        display_type = self.request.params.get('display', self.display_type)
        return '{0}?display={1}'.format(self.request.route_url(route), display_type)


@notfound_view_config(renderer='../templates/notfound.pt')
def notfound_view(request):
    """404 Not Found view"""
    return dict()


@view_config(context=EC2ResponseError, permission=NO_PERMISSION_REQUIRED)
def ec2conn_error(exc, request):
    """Handle session timeout by redirecting to login page with notice."""
    msg = exc.args[0] if exc.args else ""
    if isinstance(msg, int) and msg == 403:
        notice = _(u'Your session has timed out.')
        request.session.flash(notice, queue='warning')
        # Empty Beaker cache to clear connection objects
        BaseView.invalidate_cache()
        location = request.route_url('login')
        return HTTPFound(location=location)
