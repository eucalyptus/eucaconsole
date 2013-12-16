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
        id=(u'key-name'),
        label=_(u'Name'),
        validators=[validators.Required(message=name_error_msg), validators.Length(min=1, max=255)],
    )
    key_material = wtforms.TextAreaField(
        id=(u'key-import-contents'),
        label=_(u'Public SSH Key Content'),
        # NEED A WAY TO SELECTIVELY VALIDATE DEPENDING WHICH FORM WAS CHOSEN, CREATE VS. IMPORT
        #validators=[validators.Length(min=1)],
    )

    def __init__(self, request, keypair=None, **kwargs):
        super(KeyPairForm, self).__init__(request, **kwargs)
        self.request = request
        self.name.error_msg = self.name_error_msg  # Used for Foundation Abide error message
        if keypair is not None:
            self.name.data = keypair.name
#            self.key_material.data = keypair.key_material if keypair.key_material else ''

class KeyPairDeleteForm(BaseSecureForm):
    """KeyPair deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


