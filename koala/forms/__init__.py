# -*- coding: utf-8 -*-
"""
Base Forms

IMPORTANT: All forms needing CSRF protection should inherit from BaseSecureForm

"""
from wtforms.ext.csrf import SecureForm


class BaseSecureForm(SecureForm):
    def __init__(self, request, **kwargs):
        self.request = request
        super(BaseSecureForm, self).__init__(**kwargs)

    def generate_csrf_token(self, csrf_context):
        return self.request.session.get_csrf_token()

