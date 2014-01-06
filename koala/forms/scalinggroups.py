# -*- coding: utf-8 -*-
"""
Forms for Scaling Group 

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class ScalingGroupDeleteForm(BaseSecureForm):
    """ScalingGroup deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


