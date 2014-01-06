# -*- coding: utf-8 -*-
"""
Forms for Images 

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class ImageForm(BaseSecureForm):
    """Image form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
       Only need to initialize as a secure form to generate CSRF token
    """
    pass

