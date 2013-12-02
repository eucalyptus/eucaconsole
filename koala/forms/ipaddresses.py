# -*- coding: utf-8 -*-
"""
Forms for Elastic IP operations

"""
import wtforms
from wtforms import validators, widgets

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class AllocateIPsForm(BaseSecureForm):
    """Allocate IP Addresses form, used on IP Addresses landing page in modal dialog"""
    ipcount_error_msg = _(u'Invalid number')
    ipcount = wtforms.TextField(
        label=_(u'Number to allocate:'),
        validators=[validators.Required(message=ipcount_error_msg)],
        widget=widgets.TextInput(),
    )


class AssociateIPForm(BaseSecureForm):
    """Associate an Elastic IP with an instance"""
    instance_id = wtforms.SelectField(label=_(u'Instance:'))


class DisassociateIPForm(BaseSecureForm):
    """No fields required here except the CSRF token"""
    pass


class ReleaseIPForm(BaseSecureForm):
    """No fields required here except the CSRF token"""
    pass

