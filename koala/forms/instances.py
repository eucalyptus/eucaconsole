# -*- coding: utf-8 -*-
"""
Forms for Instances

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm
from ..constants.instances import AWS_INSTANCE_TYPE_CHOICES, EUCA_INSTANCE_TYPE_CHOICES


class InstanceForm(BaseSecureForm):
    """Instance form (to update an existing instance)
       Form to launch an instance is in LaunchInstanceForm
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
        ipaddress_choices = [empty_choice] if self.instance.ip_address else []
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


class LaunchInstanceForm(BaseSecureForm):
    """Launch instance form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
             The block device mappings are also pulled in via a panel
    """
    number_error_msg = _(u'Number of instances is required')
    number = wtforms.TextField(
        label=_(u'Number of instances'),
        validators=[validators.Required(message=number_error_msg)],
    )
    names = wtforms.TextField(label=_(u'Instance name(s)'))
    instance_type_error_msg = _(u'Instance type is required')
    instance_type = wtforms.SelectField(
        label=_(u'Instance type'),
        validators=[validators.Required(message=instance_type_error_msg)],
    )
    zone_error_msg = _(u'Availability zone is required')
    zone = wtforms.SelectField(
        label=_(u'Availability zone'),
        validators=[validators.Required(message=zone_error_msg)],
    )
    keypair_error_msg = _(u'Key pair is required')
    keypair = wtforms.SelectField(
        label=_(u'Key name'),
        validators=[validators.Required(message=keypair_error_msg)],
    )
    securitygroup_error_msg = _(u'Security group is required')
    securitygroup = wtforms.SelectField(
        label=_(u'Security group'),
        validators=[validators.Required(message=securitygroup_error_msg)],
    )
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    kernel_id = wtforms.SelectField(label=_(u'Kernel ID'))
    ramdisk_id = wtforms.SelectField(label=_(u'RAM disk ID (RAMFS)'))
    monitoring_enabled = wtforms.BooleanField(label=_(u'Enable detailed monitoring'))

    def __init__(self, request, image=None, conn=None, **kwargs):
        super(LaunchInstanceForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.image = image
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.set_error_messages()

        if image is not None:
            self.kernel_id.data = image.kernel_id or ''
            self.ramdisk_id.data = image.ramdisk_id or ''

        if conn is not None:
            self.set_instance_type_choices()
            self.set_availability_zone_choices()
            self.set_keypair_choices()
            self.set_securitygroup_choices()
            self.set_kernel_choices()
            self.set_ramdisk_choices()

    def set_error_messages(self):
        self.number.error_msg = self.number_error_msg
        self.instance_type.error_msg = self.instance_type_error_msg
        self.zone.error_msg = self.zone_error_msg
        self.keypair.error_msg = self.keypair_error_msg
        self.securitygroup.error_msg = self.securitygroup_error_msg

    def set_instance_type_choices(self):
        choices = [('', _(u'select...'))]
        if self.cloud_type == 'euca':
            # TODO: Pull instance types using DescribeInstanceTypes
            choices += EUCA_INSTANCE_TYPE_CHOICES
        elif self.cloud_type == 'aws':
            choices += AWS_INSTANCE_TYPE_CHOICES
        self.instance_type.choices = choices

    def set_availability_zone_choices(self):
        choices = []
        zones = self.conn.get_all_zones()  # TODO: cache me
        for zone in zones:
            choices.append((zone.name, zone.name))
        if not zones:
            choices.append(('', _(u'There are no availability zones')))
        self.zone.choices = sorted(set(choices))

    def set_keypair_choices(self):
        choices = []
        keypairs = self.conn.get_all_key_pairs()  # TODO: cache me
        for keypair in keypairs:
            choices.append((keypair.name, keypair.name))
        self.keypair.choices = sorted(set(choices))

    def set_securitygroup_choices(self):
        choices = []
        security_groups = self.conn.get_all_security_groups()  # TODO: cache me
        for sgroup in security_groups:
            if sgroup.id:
                choices.append((sgroup.id, sgroup.name))
        if not security_groups:
            choices.append(('', 'default'))
        self.securitygroup.choices = sorted(set(choices))

    def set_kernel_choices(self):
        choices = [('', _(u'Use default from image'))]
        kernel_images = self.conn.get_all_kernels()  # TODO: cache me
        for image in kernel_images:
            if image.kernel_id:
                choices.append((image.kernel_id, image.kernel_id))
        self.kernel_id.choices = sorted(set(choices))

    def set_ramdisk_choices(self):
        choices = [('', _(u'Use default from image'))]
        ramdisk_images = self.conn.get_all_ramdisks()  # TODO: cache me
        for image in ramdisk_images:
            if image.ramdisk_id:
                choices.append((image.ramdisk_id, image.ramdisk_id))
        self.ramdisk_id.choices = sorted(set(choices))


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
    """CSRF-protected form to attach a volume to an instance
       Note: This is for attaching a volume on the instance detail page
             The form to attach a volume to any instance from the volume detail page is at forms.volumes.AttachForm
    """
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

    def __init__(self, request, instance=None, conn=None, **kwargs):
        super(AttachVolumeForm, self).__init__(request, **kwargs)
        self.request = request
        self.conn = conn
        self.instance = instance
        self.volume_id.error_msg = self.volume_error_msg
        self.device.error_msg = self.device_error_msg
        if conn is not None:
            self.set_volume_choices()
            if self.instance is not None:
                self.device.data = self.suggest_next_device_name(self.instance.id)

    def set_volume_choices(self):
        """Populate volume field with volumes available to attach"""
        choices = [('', _(u'select...'))]
        for volume in self.conn.get_all_volumes():
            if self.instance and volume.zone == self.instance.placement and volume.attach_data.status is None:
                name_tag = volume.tags.get('Name')
                extra = ' ({name})'.format(name=name_tag) if name_tag else ''
                vol_name = '{id}{extra}'.format(id=volume.id, extra=extra)
                choices.append((volume.id, vol_name))
        if len(choices) == 1:
            choices = [('', _(u'No available volumes in the availability zone'))]
        self.volume_id.choices = choices

    def suggest_next_device_name(self, instance_id):
        instances = self.conn.get_only_instances([instance_id]);
        if instances is None:
            return 'error'
        mappings = instances[0].block_device_mapping
        for i in range(0, 10):   # Test names with char 'f' to 'p'
            dev_name = '/dev/sd'+str(unichr(102+i))
            try:
                mappings[dev_name]
            except KeyError:
                return dev_name
        return 'error'


class DetachVolumeForm(BaseSecureForm):
    """CSRF-protected form to detach a volume from an instance"""
    pass

