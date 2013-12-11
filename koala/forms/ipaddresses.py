# -*- coding: utf-8 -*-
"""
Forms for Elastic IP operations

"""
import wtforms
from wtforms import validators, widgets

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class AllocateIPsForm(BaseSecureForm):
    """Allocate IP Addresses form, used on IP Addresses landing page in modal dialog"""
    ipcount_error_msg = _(u'Invalid number')
    ipcount = wtforms.TextField(
        label=_(u'Number to allocate:'),
        validators=[validators.Required(message=ipcount_error_msg)],
        widget=widgets.TextInput(),
    )


class AssociateIPForm(BaseSecureForm):
    """Associate an Elastic IP with an instance"""
    instance_id = wtforms.SelectField(label=_(u'Instance:'))

    def __init__(self, request, elastic_ip=None, conn=None, **kwargs):
        super(AssociateIPForm, self).__init__(request, **kwargs)
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.elastic_ip = elastic_ip
        self.conn = conn
        self.instance_id.choices = self.get_instance_choices()

    def get_instance_choices(self):
        choices = [('', _(u'Select instance...'))]
        if self.conn and self.elastic_ip:
            for instance in self.conn.get_only_instances():
                if instance.ip_address != self.elastic_ip.public_ip:
                    value = instance.id
                    name_tag = instance.tags.get('Name')
                    label = '{id}{name}'.format(
                        id=instance.id,
                        name=' ({0})'.format(name_tag) if name_tag else ''
                    )
                    choices.append((value, label))
        return choices


class DisassociateIPForm(BaseSecureForm):
    """No fields required here except the CSRF token"""
    pass


class ReleaseIPForm(BaseSecureForm):
    """No fields required here except the CSRF token"""
    pass

