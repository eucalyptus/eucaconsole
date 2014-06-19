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
Forms for Images 

"""
import wtforms
from ..constants.images import EUCA_IMAGE_OWNER_ALIAS_CHOICES, AWS_IMAGE_OWNER_ALIAS_CHOICES

from ..i18n import _
from . import BaseSecureForm


class ImageForm(BaseSecureForm):
    """Image form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


class DeregisterImageForm(BaseSecureForm):
    """
    Deregister image form
    Note: delete_snapshot option only applies to EBS-backed images
    """
    delete_snapshot = wtforms.BooleanField(label=_(u'Delete snapshot'))


class ImagesFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    owner_alias = wtforms.SelectField(label=_(u'Images owned by'))
    platform = wtforms.SelectMultipleField(label=_(u'Platform'))
    root_device_type = wtforms.SelectMultipleField(label=_(u'Root device type'))
    architecture = wtforms.SelectMultipleField(label=_(u'Architecture'))
    tags = wtforms.TextField(label=_(u'Tags'))

    def __init__(self, request, cloud_type='euca', **kwargs):
        super(ImagesFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.cloud_type = cloud_type
        self.owner_alias.choices = self.get_owner_choices()
        self.platform.choices = self.get_platform_choices()
        self.root_device_type.choices = self.get_root_device_type_choices()
        self.architecture.choices = self.get_architecture_choices()
        if cloud_type == 'aws' and not self.request.params.get('owner_alias'):
            self.owner_alias.data = 'amazon'  # Default to Amazon AMIs on AWS

    def get_owner_choices(self):
        owner_choices = EUCA_IMAGE_OWNER_ALIAS_CHOICES
        if self.cloud_type == 'aws':
            owner_choices = AWS_IMAGE_OWNER_ALIAS_CHOICES
        return owner_choices

    def get_platform_choices(self):
        if self.cloud_type == 'euca':
            return (
                ('linux', 'Linux'),
                ('windows', 'Windows'),
            )
        else:
            return ('windows', 'Windows'),

    @staticmethod
    def get_root_device_type_choices():
        return (
            ('ebs', 'EBS'),
            ('instance-store', 'Instance-store'),
        )

    @staticmethod
    def get_architecture_choices():
        return (
            ('x86_64', '64-bit'),
            ('i386', '32-bit'),
        )

