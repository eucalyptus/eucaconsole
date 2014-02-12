# -*- coding: utf-8 -*-
"""
Forms for IAM policies

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from ..forms import BaseSecureForm


class IAMPolicyWizardForm(BaseSecureForm):
    """Create IAM Policy form"""

    name_error_msg = _(u'Name is required')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.InputRequired(message=name_error_msg)],
    )
    policy = wtforms.TextAreaField(label=_(u'Policy'))
    policy_file = wtforms.FileField(label=_(u''))

    def __init__(self, request, conn=None, **kwargs):
        super(IAMPolicyWizardForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.set_error_messages()

    def set_error_messages(self):
        self.name.error_msg = self.name_error_msg

