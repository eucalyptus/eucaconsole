# -*- coding: utf-8 -*-
"""
Forms for Security Groups

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm
from ..constants.instances import AWS_INSTANCE_TYPE_CHOICES, EUCA_INSTANCE_TYPE_CHOICES


class InstanceForm(BaseSecureForm):
    """Instance form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
    """
    instance_type_error_msg = _(u'Instance type is required')
    instance_type = wtforms.SelectField(
        label=_(u'Instance type'),
        validators=[validators.Required(message=instance_type_error_msg)],
    )
    ip_address = wtforms.SelectField(label=_(u'Public IP address'))
    monitored = wtforms.BooleanField(label=_(u'Monitoring enabled'))

    def __init__(self, request, instance=None, conn=None, **kwargs):
        super(InstanceForm, self).__init__(request, **kwargs)
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.instance = instance
        self.conn = conn
        self.instance_type.error_msg = self.instance_type_error_msg

        if instance is not None:
            self.instance_type.data = instance.instance_type
            self.ip_address.data = instance.ip_address or ''
            self.monitored.data = instance.monitored

            if conn is not None:
                self.set_ipaddress_choices()
                self.set_instance_type_choices()

    def set_ipaddress_choices(self):
        """Set IP address choices
           Note: we're adding the instances' current address to the choices list,
               as it may not be in the get_all_addresses fetch.
        """
        empty_choice = ('', _(u'Unassign address...'))
        ipaddress_choices = [empty_choice]
        existing_ip_choices = [(eip.public_ip, eip.public_ip) for eip in self.conn.get_all_addresses()]
        ipaddress_choices += existing_ip_choices
        ipaddress_choices += [(self.instance.ip_address, self.instance.ip_address)]
        self.ip_address.choices = sorted(set(ipaddress_choices))

    def set_instance_type_choices(self):
        choices = [('', _(u'select...'))]
        if self.cloud_type == 'euca':
            choices += EUCA_INSTANCE_TYPE_CHOICES
        elif self.cloud_type == 'aws':
            choices += AWS_INSTANCE_TYPE_CHOICES
        self.instance_type.choices = choices


class StopInstanceForm(BaseSecureForm):
    """CSRF-protected form to stop an instance"""
    pass


class StartInstanceForm(BaseSecureForm):
    """CSRF-protected form to start an instance"""
    pass


class RebootInstanceForm(BaseSecureForm):
    """CSRF-protected form to reboot an instance"""
    pass


class TerminateInstanceForm(BaseSecureForm):
    """CSRF-protected form to terminate an instance"""
    pass


class AttachVolumeForm(BaseSecureForm):
    """CSRF-protected form to attach a volume to an instance"""
    volume_error_msg = _(u'Volume is required')
    volume_id = wtforms.SelectField(
        label=_(u'Volume'),
        validators=[validators.Required(message=volume_error_msg)],
    )
    device_error_msg = _(u'Device is required')
    device = wtforms.TextField(
        label=_(u'Device'),
        validators=[validators.Required(message=device_error_msg)],
    )

    def __init__(self, request, conn=None, **kwargs):
        super(AttachVolumeForm, self).__init__(request, **kwargs)
        self.request = request
        self.conn = conn
        self.device.error_msg = self.device_error_msg
        if conn is not None:
            self.set_volume_choices()

    def set_volume_choices(self):
        """Populate volume field with volumes available to attach"""
        choices = [('', _(u'select...'))]
        choices += [(vol.id, vol.id) for vol in self.conn.get_all_volumes() if vol.attach_data.status is None]
        self.volume_id.choices = choices


class DetachVolumeForm(BaseSecureForm):
    """CSRF-protected form to detach a volume from an instance"""
    pass

