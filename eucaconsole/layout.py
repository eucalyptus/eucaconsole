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
Layout configuration via pyramid_layout
See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html

"""
from collections import namedtuple
from urllib import urlencode

from beaker.cache import cache_region
from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.settings import asbool

from .constants import AWS_REGIONS
from .forms.login import EucaLogoutForm
from .i18n import _
from .models import Notification

try:
    from version import __version__
except ImportError:
    __version__ = 'DEVELOPMENT'


class MasterLayout(object):
    site_title = "Eucalyptus Management Console"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.version = __version__
        self.home_url = request.application_url
        self.help_url = request.registry.settings.get('help.url')
        self.support_url = request.registry.settings.get('support.url') or "http://support.eucalyptus.com"
        self.aws_enabled = asbool(request.registry.settings.get('aws.enabled'))
        self.aws_regions = AWS_REGIONS
        self.default_region = request.registry.settings.get('aws.default.region')
        self.browser_password_save = 'true' if asbool(request.registry.settings.get('browser.password.save')) else 'false'
        self.cloud_type = request.session.get('cloud_type')
        self.selected_region = self.request.session.get('region', self.default_region)
        self.selected_region_label = self.get_selected_region_label(self.selected_region)
        self.username = self.request.session.get('username')
        self.account = self.request.session.get('account')
        self.username_label = self.request.session.get('username_label')
        self.user_access = True
        self.group_access = True
        self.role_access = True
        self.euca_logout_form = EucaLogoutForm(request=self.request)
        self.date_format = _(u'%I:%M:%S %p %b %d %Y')
        self.angular_date_format = _(u'hh:mm:ss a MMM d yyyy')
        self.tag_pattern_key = '^(?!aws:).{0,128}$'
        self.tag_pattern_value = '^(?!aws:).{0,256}$'
        self.integer_gt_zero_pattern = '^[1-9]\d*$'
        self.non_negative_pattern = '^[0-9]\d*$'
        self.cidr_pattern = '{0}{1}'.format(
            '^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}',
            '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])(\/\d+)$'
        )
        self.querystring = self.get_query_string()
        self.help_html_dir = 'eucaconsole:static/html/help/'

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
        # Add custom error messages via self.request.error_messages = [message_1, message_2, ...] in the view
        error_messages = getattr(self.request, 'error_messages', [])
        for error in error_messages:
            queue = Notification.ERROR
            notifications.append(
                notification(message=error, type=queue, style=Notification.FOUNDATION_STYLES.get(queue))
            )
        return notifications

    def get_query_string(self):
        if self.request.GET:
            return '?{0}'.format(urlencode(self.request.GET))
        return ''

    def help_path(self, help_html):
        path = self.help_html_dir + help_html;
        return self.request.static_path(path);

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
