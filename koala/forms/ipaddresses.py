# -*- coding: utf-8 -*-
"""
Forms for Elastic IP operations

"""
import wtforms
from wtforms import validators, widgets

from . import BaseSecureForm


class AllocateIPsForm(BaseSecureForm):
    """Allocate IP Addresses form, used on IP Addresses landing page in modal dialog"""
    ipcount_error_msg = u'Invalid number'
    ipcount = wtforms.TextField(
        'Number to allocate:',
        validators=[validators.Required(message=ipcount_error_msg)],
        widget=widgets.TextInput(),
    )


