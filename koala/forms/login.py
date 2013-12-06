# -*- coding: utf-8 -*-
"""
Eucalyptus and AWS login forms

"""
import wtforms
from wtforms import validators, widgets

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class EucaLoginForm(BaseSecureForm):
    account = wtforms.TextField(
        _(u'Account Name'), validators=[validators.Required(message=_(u'Account name is required'))])
    username = wtforms.TextField(
        _(u'Username'), validators=[validators.Required(message=_(u'Username is required'))])
    password = wtforms.PasswordField(
        _(u'Password'), validators=[validators.Required(message=_(u'Password is required'))])


class AWSLoginForm(BaseSecureForm):
    access_key = wtforms.TextField(
        _(u'Access key ID'), validators=[validators.Required(message=_(u'Access key is required'))])
    secret_key = wtforms.PasswordField(
        _(u'Secret key'), validators=[validators.Required(message=_(u'Secret key is required'))])

class EucaChangePasswordForm(BaseSecureForm):
    password = wtforms.PasswordField(
        _(u'Password'), validators=[validators.Required(message=_(u'Password is required'))],
        widget=widgets.PasswordInput())
    new_password = wtforms.PasswordField(
        _(u'New Password'),
        validators=[
            validators.Required(message=_(u'New Password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())
    new_password2 = wtforms.PasswordField(
        _(u'New Password'),
        validators=[
            validators.Required(message=_(u'New Password is required')),
            validators.Length(min=6, message=_(u'Password must be more than 6 characters'))
        ],
        widget=widgets.PasswordInput())
        
