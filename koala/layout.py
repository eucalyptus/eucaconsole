# -*- coding: utf-8 -*-
"""
Layout configuration via pyramid_layout
See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html

"""
from collections import namedtuple
from urlparse import urlparse

from beaker.cache import cache_region
from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.settings import asbool

from .constants import AWS_REGIONS
from .models import Notification


class MasterLayout(object):
    site_title = "Eucalyptus Management Console"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.home_url = request.application_url
        self.help_url = request.registry.settings.get('help.url')
        self.aws_enabled = asbool(request.registry.settings.get('aws.enabled'))
        self.aws_regions = AWS_REGIONS
        self.default_region = request.registry.settings.get('aws.default.region')
        self.cloud_type = request.session.get('cloud_type')
        self.selected_region = self.request.session.get('region', self.default_region)
        self.selected_region_label = self.get_selected_region_label(self.selected_region)
        self.username_label = self.request.session.get('username_label')
        self.tableview_url = self.get_datagridview_url('tableview')
        self.gridview_url = self.get_datagridview_url('gridview')

    def get_notifications(self):
        """Get notifications, categorized by message type ('info', 'success', 'warning', or 'error')
        To add a success notification, use self.request.session.flash(msg, 'success')
        See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html#using-the-session-flash-method
        """
        notifications = []
        notification = namedtuple('Notification', ['message', 'type', 'style'])
        for queue in Notification.TYPES:
            for notice in self.request.session.pop_flash(queue=queue):
                notifications.append(
                    notification(message=notice, type=queue, style=Notification.FOUNDATION_STYLES.get(queue)))
        return notifications

    def get_datagridview_url(self, display):
        """Convience property to get tableview or gridview URL for landing pages"""
        current_url = self.request.current_route_url()
        parsed_url = urlparse(current_url)
        otherview = 'gridview' if display == 'tableview' else 'tableview'
        if 'display' in parsed_url.query:
            return current_url.replace(otherview, display)
        else:
            return '{url}?display={view}'.format(url=current_url, view=display)

    @staticmethod
    @cache_region('extra_long_term', 'selected_region_label')
    def get_selected_region_label(region_name):
        """Get the label from the selected region, pulling from Beaker cache"""
        regions = [reg for reg in AWS_REGIONS if reg.get('name') == region_name]
        if regions:
            return regions[0].get('label')
        return ''

    @reify
    def global_macros(self):
        renderer = get_renderer("templates/macros.pt")
        return renderer.implementation().macros
