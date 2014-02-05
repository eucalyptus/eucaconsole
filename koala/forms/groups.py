# -*- coding: utf-8 -*-
"""
Forms for Groups 

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class GroupForm(BaseSecureForm):
    """Group form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
       Only need to initialize as a secure form to generate CSRF token
    """
    group_name_error_msg = ''
    group_name = wtforms.TextField(
        id=u'group-name',
        label=_(u'Name'),
        validators=[validators.Length(min=1, max=255)],
    )

    path_error_msg = ''
    path = wtforms.TextField(
        id=u'group-path',
        label=_(u'Path'),
        validators=[validators.Length(min=1, max=255)],
    )

    users_error_msg = ''
    users = wtforms.TextField(
        id=u'group-users',
        label=(u''),
        validators=[],
    )

    def __init__(self, request, group=None, **kwargs):
        super(GroupForm, self).__init__(request, **kwargs)
        self.request = request
        self.group_name.error_msg = self.group_name_error_msg  # Used for Foundation Abide error message
        self.path_error_msg = self.path_error_msg
        if group is not None:
            self.group_name.data = group.group_name
            self.path.data = group.path


