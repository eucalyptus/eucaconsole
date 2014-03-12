# -*- coding: utf-8 -*-
"""
Forms for Images 

"""
import wtforms
from ..constants.images import EUCA_IMAGE_OWNER_ALIAS_CHOICES, AWS_IMAGE_OWNER_ALIAS_CHOICES

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class ImageForm(BaseSecureForm):
    """Image form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


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

