# -*- coding: utf-8 -*-
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

