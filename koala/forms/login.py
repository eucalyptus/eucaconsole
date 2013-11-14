# -*- coding: utf-8 -*-
"""
Eucalyptus and AWS login forms

"""
import wtforms
from wtforms import validators

from . import BaseSecureForm


class EucaLoginForm(BaseSecureForm):
    account = wtforms.TextField(
        'Account Name', validators=[validators.Required(message=u'Account name is required')])
    username = wtforms.TextField(
        'Username', validators=[validators.Required(message=u'Username is required')])
    password = wtforms.PasswordField(
        'Password', validators=[validators.Required(message=u'Password is required')])


class AWSLoginForm(BaseSecureForm):
    access_key = wtforms.TextField(
        'Access key ID', validators=[validators.Required(message=u'Access key is required')])
    secret_key = wtforms.PasswordField(
        'Secret key', validators=[validators.Required(message=u'Secret key is required')])
