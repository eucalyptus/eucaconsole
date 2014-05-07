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
Core models

"""
from pyramid.security import Allow, Authenticated


class SiteRootFactory(object):
    """Every Pyramid site that implements authentication/authorization needs a root factory,
       We may implement ACLs at the resource level, but the site-level ACL is defined here
    """
    __acl__ = [
        (Allow, Authenticated, 'view')
    ]

    def __init__(self, request):
        pass


class LandingPageFilter(object):
    """Filter for landing pages

    :ivar key: the key to filter on (matches item attribute to filter)
    :ivar name: The label to display in the filter selection

    """
    def __init__(self, key=None, name=None, choices=None):
        self.key = key
        self.name = name
        self.choices = choices or []


class Notification(object):
    """Standardize notification types for flash messaging"""
    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
    TYPES = (INFO, SUCCESS, WARNING, ERROR)
    # Map notification queues to Zurb Foundation alert box styles
    # See http://foundation.zurb.com/docs/components/alert-boxes.html
    FOUNDATION_STYLES = {
        INFO: 'secondary',
        SUCCESS: 'success',
        WARNING: 'warning',
        ERROR: 'alert',
    }

