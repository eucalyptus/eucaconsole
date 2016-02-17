# -*- coding: utf-8 -*-
# Copyright 2013-2015 Hewlett Packard Enterprise Development LP
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
Forms for Cloud Formations

"""
import wtforms
from wtforms import validators

from ..i18n import _
from . import BaseSecureForm, TextEscapedField, CFSampleTemplateManager


class StacksCreateForm(BaseSecureForm):
    """Stacks creation form.
       Only need to initialize as a secure form to generate CSRF token
    """
    name_error_msg = _(u"""Name is required, must begin with a letter, and may contain only letters,
        numbers, and/or hyphens. Length must not exceed 255 characters.""")
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.InputRequired(message=name_error_msg)],
    )
    sample_template = wtforms.SelectField(label='')
    template_file_helptext = _(u'Template file may not exceed 16 KB')
    template_file = wtforms.FileField(label='')

    def __init__(self, request, s3_bucket, **kwargs):
        super(StacksCreateForm, self).__init__(request, **kwargs)
        self.name.error_msg = self.name_error_msg
        self.template_file.help_text = self.template_file_helptext
        mgr = CFSampleTemplateManager(s3_bucket)
        self.sample_template.choices = mgr.get_template_options()


class StacksUpdateForm(BaseSecureForm):
    """Stacks update form.
       Only need to initialize as a secure form to generate CSRF token
    """
    template_file_helptext = _(u'Template file may not exceed 16 KB')
    template_file = wtforms.FileField(label='')

    def __init__(self, request, s3_bucket, **kwargs):
        super(StacksCreateForm, self).__init__(request, **kwargs)
        self.template_file.help_text = self.template_file_helptext


class StacksDeleteForm(BaseSecureForm):
    """Stacks deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


class StacksFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    tags = TextEscapedField(label=_(u'Tags'))

    def __init__(self, request, **kwargs):
        super(StacksFiltersForm, self).__init__(request, **kwargs)
        self.facets = [
            {'name': 'status', 'label': _(u'Status'), 'options': [
                {'key': 'create-in-progress', 'label': _(u'Create in progress')},
                {'key': 'create-complete', 'label': _(u'Create complete')},
                {'key': 'create-failed', 'label': _(u'Create failed')},
                {'key': 'rollback-in-progress', 'label': _(u'Rollback in progress')},
                {'key': 'rollback-complete', 'label': _(u'Rollback complete')},
                {'key': 'rollback-failed', 'label': _(u'Rollback failed')},
                {'key': 'delete-in-progress', 'label': _(u'Delete in progress')},
                {'key': 'delete-complete', 'label': _(u'Delete complete')},
                {'key': 'delete-failed', 'label': _(u'Delete failed')},
            ]}
        ]
