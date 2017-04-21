# -*- coding: utf-8 -*-
# Copyright 2013-2017 Ent. Services Development Corporation LP
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

