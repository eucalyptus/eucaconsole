# -*- coding: utf-8 -*-
"""
Forms for Security Groups

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class SecurityGroupForm(BaseSecureForm):
    """Security Group form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
    """
    name_error_msg = _(u'Name is required')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.Required(message=name_error_msg)],
    )
    desc_error_msg = _(u'Description is required')
    description = wtforms.TextAreaField(
        label=_(u'Description'),
        validators=[
            validators.Required(message=desc_error_msg),
            validators.Length(max=255, message=_(u'Description must be less than 255 characters'))
        ],
    )

    def __init__(self, request, security_group=None, **kwargs):
        super(SecurityGroupForm, self).__init__(request, **kwargs)
        self.name.error_msg = self.name_error_msg  # Used for Foundation Abide error message
        self.description.error_msg = self.desc_error_msg  # Used for Foundation Abide error message
        if security_group is not None:
            self.name.data = security_group.name
            self.description.data = security_group.description


class SecurityGroupDeleteForm(BaseSecureForm):
    """Security Group deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass
