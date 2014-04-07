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
    instance_type = wtforms.SelectField(label=_(u'Instance type'))
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    ip_address = wtforms.SelectField(label=_(u'Public IP address'))
    monitored = wtforms.BooleanField(label=_(u'Monitoring enabled'))
    kernel = wtforms.SelectField(label=_(u'Kernel ID'))
    ramdisk = wtforms.SelectField(label=_(u'RAM disk ID (ramfs)'))
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
        self.kernel.choices = self.choices_manager.kernels()
        self.ramdisk.choices = self.choices_manager.ramdisks()


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
            validators.InputRequired(message=number_error_msg),
            validators.NumberRange(min=1, max=10),  # Restrict num instances that can be launched in one go
        ],
    )
    instance_type_error_msg = _(u'Instance type is required')
    instance_type = wtforms.SelectField(
        label=_(u'Instance type'),
        validators=[validators.InputRequired(message=instance_type_error_msg)],
    )
    zone = wtforms.SelectField(label=_(u'Availability zone'))
    keypair_error_msg = _(u'Key pair is required')
    keypair = wtforms.SelectField(
        label=_(u'Key name')
    )
    securitygroup_error_msg = _(u'Security group is required')
    securitygroup = wtforms.SelectField(
        label=_(u'Security group'),
        validators=[validators.InputRequired(message=securitygroup_error_msg)],
    )
    role = wtforms.SelectField()
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    userdata_file_helptext = _(u'User data file may not exceed 16 KB')
    userdata_file = wtforms.FileField(label=_(u''))
    kernel_id = wtforms.SelectField(label=_(u'Kernel ID'))
    ramdisk_id = wtforms.SelectField(label=_(u'RAM disk ID (RAMFS)'))
    monitoring_enabled = wtforms.BooleanField(label=_(u'Enable monitoring'))
    private_addressing = wtforms.BooleanField(label=_(u'Use private addressing only'))

    def __init__(self, request, image=None, securitygroups=None, conn=None, iam_conn=None, **kwargs):
        super(LaunchInstanceForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.iam_conn = iam_conn
        self.image = image
        self.securitygroups = securitygroups
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.set_error_messages()
        self.monitoring_enabled.data = True
        self.choices_manager = ChoicesManager(conn=conn)
        self.set_help_text()
        self.set_choices(request)

        if image is not None:
            self.image_id.data = self.image.id
            self.kernel_id.data = image.kernel_id or ''
            self.ramdisk_id.data = image.ramdisk_id or ''

    def set_help_text(self):
        self.userdata_file.help_text = self.userdata_file_helptext

    def set_choices(self, request):
        self.instance_type.choices = self.choices_manager.instance_types(cloud_type=self.cloud_type, add_blank=False)
        region = request.session.get('region')
        self.zone.choices = self.get_availability_zone_choices(region)
        self.keypair.choices = self.get_keypair_choices()
        self.securitygroup.choices = self.choices_manager.security_groups(securitygroups=self.securitygroups, add_blank=False)
        self.role.choices = ChoicesManager(self.iam_conn).roles(add_blank=False)
        self.kernel_id.choices = self.choices_manager.kernels(image=self.image)
        self.ramdisk_id.choices = self.choices_manager.ramdisks(image=self.image)

        # Set default choices where applicable, defaulting to first non-blank choice
        if self.cloud_type == 'aws' and len(self.zone.choices) > 1:
            self.zone.data = self.zone.choices[1][0]
        # Set the defailt option to be "No Keypair" and "Default" security group
        if len(self.securitygroup.choices) > 1:
            self.securitygroup.data = "default"
        if len(self.keypair.choices) > 1:
            self.keypair.data = self.keypair.choices[1][0]

    def set_error_messages(self):
        self.number.error_msg = self.number_error_msg
        self.instance_type.error_msg = self.instance_type_error_msg
        self.keypair.error_msg = self.keypair_error_msg
        self.securitygroup.error_msg = self.securitygroup_error_msg

    def get_keypair_choices(self):
        choices = self.choices_manager.keypairs(add_blank=False, no_keypair_option=True)
        return choices

    def get_availability_zone_choices(self, region):
        choices = [('', _(u'No preference'))]
        choices.extend(self.choices_manager.availability_zones(region, add_blank=False))
        return choices


class LaunchMoreInstancesForm(BaseSecureForm):
    """Form class for launch more instances like this one"""
    number_error_msg = _(u'Number of instances is required')
    number = wtforms.IntegerField(
        label=_(u'How many instances would you like to launch?'),
        validators=[
            validators.InputRequired(message=number_error_msg),
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


class BatchTerminateInstancesForm(BaseSecureForm):
    """CSRF-protected form to batch-terminate instances"""
    pass


class AttachVolumeForm(BaseSecureForm):
    """CSRF-protected form to attach a volume to an instance
       Note: This is for attaching a volume on the instance detail page
             The form to attach a volume to any instance from the volume detail page is at forms.volumes.AttachForm
    """
    volume_error_msg = _(u'Volume is required')
    volume_id = wtforms.SelectField(
        label=_(u'Volume'),
        validators=[validators.InputRequired(message=volume_error_msg)],
    )
    device_error_msg = _(u'Device is required')
    device = wtforms.TextField(
        label=_(u'Device'),
        validators=[validators.InputRequired(message=device_error_msg)],
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


class InstancesFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    state = wtforms.SelectMultipleField(label=_(u'Status'))
    availability_zone = wtforms.SelectMultipleField(label=_(u'Availability zone'))
    instance_type = wtforms.SelectMultipleField(label=_(u'Instance type'))
    root_device_type = wtforms.SelectMultipleField(label=_(u'Root device type'))
    security_group = wtforms.SelectMultipleField(label=_(u'Security group'))
    scaling_group = wtforms.SelectMultipleField(label=_(u'Scaling group'))
    tags = wtforms.TextField(label=_(u'Tags'))

    def __init__(self, request, ec2_conn=None, autoscale_conn=None, cloud_type='euca', **kwargs):
        super(InstancesFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.ec2_conn = ec2_conn
        self.autoscale_conn = autoscale_conn
        self.cloud_type = cloud_type
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        self.autoscale_choices_manager = ChoicesManager(conn=autoscale_conn)
        region = request.session.get('region')
        self.availability_zone.choices = self.get_availability_zone_choices(region)
        self.state.choices = self.get_status_choices()
        self.instance_type.choices = self.get_instance_type_choices()
        self.root_device_type.choices = self.get_root_device_type_choices()
        self.security_group.choices = self.ec2_choices_manager.security_groups(add_blank=False)
        self.scaling_group.choices = self.autoscale_choices_manager.scaling_groups(add_blank=False)

    def get_availability_zone_choices(self, region):
        return self.ec2_choices_manager.availability_zones(region, add_blank=False)

    def get_instance_type_choices(self):
        return self.ec2_choices_manager.instance_types(
            cloud_type=self.cloud_type, add_blank=False, add_description=False)

    @staticmethod
    def get_status_choices():
        return (
            ('running', 'Running'),
            ('pending', 'Pending'),
            ('stopping', 'Stopping'),
            ('stopped', 'Stopped'),
            ('shutting-down', 'Terminating'),
            ('terminated', 'Terminated'),
        )

    @staticmethod
    def get_root_device_type_choices():
        return (
            ('ebs', 'EBS'),
            ('instance-store', 'Instance-store')
        )


class AssociateIpToInstanceForm(BaseSecureForm):
    """CSRF-protected form to associate IP to an instance"""
    associate_ip_error_msg = _(u'IP is required')
    ip_address = wtforms.SelectField(
        label=_(u'IP address:'),
        validators=[validators.InputRequired(message=associate_ip_error_msg)],
    )

    def __init__(self, request, conn=None, **kwargs):
        super(AssociateIpToInstanceForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.choices_manager = ChoicesManager(conn=self.conn)
        self.ip_address.choices = self.choices_manager.elastic_ips()
        self.ip_address.error_msg = self.associate_ip_error_msg


class DisassociateIpFromInstanceForm(BaseSecureForm):
    """CSRF-protected form to disassociate IP from an instance"""
    pass

