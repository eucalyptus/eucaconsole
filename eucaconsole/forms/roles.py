# -*- coding: utf-8 -*-
"""
Forms for Roles 

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class RoleForm(BaseSecureForm):
    """Role form
    """
    role_name_error_msg = 'Role name is required'
    role_name = wtforms.TextField(
        id=u'role-name',
        label=_(u'Name'),
        validators=[validators.InputRequired(message=role_name_error_msg), validators.Length(min=1, max=255)],
    )

    path_error_msg = ''
    path = wtforms.TextField(
        id=u'role-path',
        label=_(u'Path'),
        default="/",
        validators=[validators.Length(min=1, max=255)],
    )

    def __init__(self, request, role=None, **kwargs):
        super(RoleForm, self).__init__(request, **kwargs)
        self.request = request
        self.role_name.error_msg = self.role_name_error_msg  # Used for Foundation Abide error message
        self.path_error_msg = self.path_error_msg
        if role is not None:
            self.role_name.data = role.role_name
            self.path.data = role.path


class DeleteRoleForm(BaseSecureForm):
    """CSRF-protected form to delete a role"""
    pass

