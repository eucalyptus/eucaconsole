# -*- coding: utf-8 -*-
"""
Forms for Instances

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm, ChoicesManager


class InstanceForm(BaseSecureForm):
    """Instance form (to update an existing instance)
       Form to launch an instance is in LaunchInstanceForm
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
    """
    instance_type_error_msg = _(u'Instance type is required')
    instance_type = wtforms.SelectField(
        label=_(u'Instance type')
    )
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    ip_address = wtforms.SelectField(label=_(u'Public IP address'))
    monitored = wtforms.BooleanField(label=_(u'Monitoring enabled'))
    kernel = wtforms.SelectField(
        label=_(u'Kernel ID')
    )
    ramdisk = wtforms.SelectField(
        label=_(u'RAM disk ID (ramfs)')
    )
    start_later = wtforms.HiddenField()

    def __init__(self, request, instance=None, conn=None, **kwargs):
        super(InstanceForm, self).__init__(request, **kwargs)
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.instance = instance
        self.conn = conn
        self.instance_type.error_msg = self.instance_type_error_msg
        self.choices_manager = ChoicesManager(conn=self.conn)
        self.set_choices()

        if instance is not None:
            self.instance_type.data = instance.instance_type
            self.ip_address.data = instance.ip_address or 'none'
            self.monitored.data = instance.monitored
            self.kernel.data = instance.kernel or ''
            self.ramdisk.data = instance.ramdisk or ''
            self.userdata.data = ''

    def set_choices(self):
        self.ip_address.choices = self.choices_manager.elastic_ips(instance=self.instance)
        self.instance_type.choices = self.choices_manager.instance_types(cloud_type=self.cloud_type)
        self.kernel.choices = self.choices_manager.kernels();
        self.ramdisk.choices = self.choices_manager.ramdisks();


class LaunchInstanceForm(BaseSecureForm):
    """Launch instance form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
             The block device mappings are also pulled in via a panel
    """
    image_id = wtforms.HiddenField(label=_(u'Image'))
    number_error_msg = _(u'Number of instances is required')
    number = wtforms.IntegerField(
        label=_(u'Number of instances'),
        validators=[
            validators.Required(message=number_error_msg),
            validators.NumberRange(min=1, max=10),  # Restrict num instances that can be launched in one go
        ],
    )
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
    userdata_file_helptext = _(u'User data file may not exceed 16 KB')
    userdata_file = wtforms.FileField(label=_(u''))
    kernel_id = wtforms.SelectField(label=_(u'Kernel ID'))
    ramdisk_id = wtforms.SelectField(label=_(u'RAM disk ID (RAMFS)'))
    monitoring_enabled = wtforms.BooleanField(label=_(u'Enable detailed monitoring'))
    private_addressing = wtforms.BooleanField(label=_(u'Use private addressing only'))

    def __init__(self, request, image=None, conn=None, **kwargs):
        super(LaunchInstanceForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.image = image
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.set_error_messages()
        self.monitoring_enabled.data = True
        self.choices_manager = ChoicesManager(conn=conn)
        self.set_help_text()
        self.set_choices()

        if image is not None:
            self.image_id.data = self.image.id
            self.kernel_id.data = image.kernel_id or ''
            self.ramdisk_id.data = image.ramdisk_id or ''

    def set_help_text(self):
        self.userdata_file.help_text = self.userdata_file_helptext

    def set_choices(self):
        self.instance_type.choices = self.choices_manager.instance_types(cloud_type=self.cloud_type)
        self.zone.choices = self.choices_manager.availability_zones()
        self.keypair.choices = self.choices_manager.keypairs()
        self.securitygroup.choices = self.choices_manager.security_groups()
        self.kernel_id.choices = self.choices_manager.kernels(image=self.image)
        self.ramdisk_id.choices = self.choices_manager.ramdisks(image=self.image)

        # Set default choices where applicable, defaulting to first non-blank choice
        if len(self.zone.choices) > 1:
            self.zone.data = self.zone.choices[1][0]
        if len(self.securitygroup.choices) > 1:
            self.securitygroup.data = self.securitygroup.choices[1][0]
        if len(self.keypair.choices) > 1:
            self.keypair.data = self.keypair.choices[1][0]

    def set_error_messages(self):
        self.number.error_msg = self.number_error_msg
        self.instance_type.error_msg = self.instance_type_error_msg
        self.zone.error_msg = self.zone_error_msg
        self.keypair.error_msg = self.keypair_error_msg
        self.securitygroup.error_msg = self.securitygroup_error_msg


class LaunchMoreInstancesForm(BaseSecureForm):
    """Form class for launch more instances like this one"""
    number_error_msg = _(u'Number of instances is required')
    number = wtforms.IntegerField(
        label=_(u'Number of instances'),
        validators=[
            validators.Required(message=number_error_msg),
            validators.NumberRange(min=1, max=10),  # Restrict num instances that can be launched in one go
        ],
    )
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    userdata_file_helptext = _(u'User data file may not exceed 16 KB')
    userdata_file = wtforms.FileField(label=_(u''))
    kernel_id = wtforms.SelectField(label=_(u'Kernel ID'))
    ramdisk_id = wtforms.SelectField(label=_(u'RAM disk ID (RAMFS)'))
    monitoring_enabled = wtforms.BooleanField(label=_(u'Enable detailed monitoring'))
    private_addressing = wtforms.BooleanField(label=_(u'Use private addressing only'))

    def __init__(self, request, image=None, conn=None, **kwargs):
        super(LaunchMoreInstancesForm, self).__init__(request, **kwargs)
        self.image = image
        self.conn = conn
        self.choices_manager = ChoicesManager(conn=conn)
        self.set_error_messages()
        self.set_help_text()
        self.set_choices()
        self.set_initial_data()

    def set_error_messages(self):
        self.number.error_msg = self.number_error_msg

    def set_help_text(self):
        self.userdata_file.help_text = self.userdata_file_helptext

    def set_choices(self):
        self.kernel_id.choices = self.choices_manager.kernels(image=self.image)
        self.ramdisk_id.choices = self.choices_manager.ramdisks(image=self.image)

    def set_initial_data(self):
        self.monitoring_enabled.data = True
        self.number.data = 1


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

    def __init__(self, request, volumes=None, instance=None, **kwargs):
        super(AttachVolumeForm, self).__init__(request, **kwargs)
        self.request = request
        self.volumes = volumes or []
        self.instance = instance
        self.volume_id.error_msg = self.volume_error_msg
        self.device.error_msg = self.device_error_msg
        self.set_volume_choices()
        if self.instance is not None:
            self.device.data = self.suggest_next_device_name()

    def set_volume_choices(self):
        """Populate volume field with volumes available to attach"""
        choices = [('', _(u'select...'))]
        for volume in self.volumes:
            if self.instance and volume.zone == self.instance.placement and volume.attach_data.status is None:
                name_tag = volume.tags.get('Name')
                extra = ' ({name})'.format(name=name_tag) if name_tag else ''
                vol_name = '{id}{extra}'.format(id=volume.id, extra=extra)
                choices.append((volume.id, vol_name))
        if len(choices) == 1:
            choices = [('', _(u'No available volumes in the availability zone'))]
        self.volume_id.choices = choices

    def suggest_next_device_name(self):
        mappings = self.instance.block_device_mapping
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

