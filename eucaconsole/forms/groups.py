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
Forms for Groups 

"""
import wtforms
from wtforms import validators

from ..i18n import _
from . import BaseSecureForm, TextEscapedField


class GroupForm(BaseSecureForm):
    """Group form
    """
    group_name_error_msg = 'Group name is required'
    group_name = TextEscapedField(
        id=u'group-name',
        label=_(u'Name'),
        validators=[validators.InputRequired(message=group_name_error_msg), validators.Length(min=1, max=255)],
    )

    path_error_msg = ''
    path = TextEscapedField(
        id=u'group-path',
        label=_(u'Path'),
        default="/",
        validators=[validators.Length(min=1, max=255)],
    )

    def __init__(self, request, group=None, **kwargs):
        super(GroupForm, self).__init__(request, **kwargs)
        self.request = request
        self.group_name.error_msg = self.group_name_error_msg  # Used for Foundation Abide error message
        self.path_error_msg = self.path_error_msg
        if group is not None:
            self.group_name.data = group.group_name
            self.path.data = group.path


class GroupUpdateForm(BaseSecureForm):
    """Group update form
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
        super(GroupUpdateForm, self).__init__(request, **kwargs)
        self.request = request
        self.group_name.error_msg = self.group_name_error_msg  # Used for Foundation Abide error message
        self.path_error_msg = self.path_error_msg
        if group is not None:
            self.group_name.data = group.group_name
            self.path.data = group.path


class DeleteGroupForm(BaseSecureForm):
    """CSRF-protected form to delete a group"""
    pass

