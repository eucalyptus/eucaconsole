# -*- coding: utf-8 -*-
"""
Forms for Key Pairs 

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class KeyPairForm(BaseSecureForm):
    """Key Pair form
    """
    name_error_msg = _(u'Name is required')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.Required(message=name_error_msg)],
    )

    def __init__(self, request, keypair=None, **kwargs):
        super(KeyPairForm, self).__init__(request, **kwargs)
        self.name.error_msg = self.name_error_msg  # Used for Foundation Abide error message
        if keypair is not None:
            self.name.data = keypair.name

