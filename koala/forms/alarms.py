# -*- coding: utf-8 -*-
"""
Forms for CloudWatch Alarms

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class CloudWatchAlarmCreateForm(BaseSecureForm):
    """Form for creating a CloudWatch alarm"""
    name_error_msg = _(u'Name is required')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[
            validators.InputRequired(message=name_error_msg),
        ],
    )

    def __init__(self, request, **kwargs):
        super(CloudWatchAlarmCreateForm, self).__init__(request, **kwargs)
        self.set_error_messages()
        self.set_choices()
        self.set_help_text()

    def set_choices(self):
        pass

    def set_error_messages(self):
        self.name.error_msg = self.name_error_msg

    def set_help_text(self):
        pass


class CloudWatchAlarmDeleteForm(BaseSecureForm):
    """CloudWatch Alarm deletion form"""
    pass

