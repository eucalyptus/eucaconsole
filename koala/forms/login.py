"""
Eucalyptus and AWS login forms

"""
import wtforms
from wtforms import validators

from . import BaseSecureForm


class EucaLoginForm(BaseSecureForm):
    account_name = wtforms.TextField(
        'Account Name', validators=[validators.Required(message=u'Account name is required')])
    username = wtforms.TextField(
        'Username', validators=[validators.Required(message=u'Username is required')])
    password = wtforms.PasswordField(
        'Password', validators=[validators.Required(message=u'Password is required')])

