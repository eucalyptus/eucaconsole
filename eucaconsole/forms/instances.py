# -*- coding: utf-8 -*-
# Copyright 2013-2014 Eucalyptus Systems, Inc.
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Forms for Instances

"""
import wtforms
from wtforms import validators

from ..i18n import _
from . import BaseSecureForm, ChoicesManager, TextEscapedField


class InstanceForm(BaseSecureForm):
    """Instance form (to update an existing instance)
       Form to launch an instance is in LaunchInstanceForm
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
    """
    name_error_msg = _(u'Not a valid name')
    name = TextEscapedField(label=_(u'Name'))
    instance_type_error_msg = _(u'Instance type is required')
    instance_type = wtforms.SelectField(label=_(u'Instance type'))
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    userdata_file_helptext = _(u'User data file may not exceed 16 KB')
    userdata_file = wtforms.FileField(label='')
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
        self.name.error_msg = self.name_error_msg
        self.instance_type.error_msg = self.instance_type_error_msg
        self.choices_manager = ChoicesManager(conn=self.conn)
        self.set_choices()
        self.userdata_file.help_text = self.userdata_file_helptext

        if instance is not None:
            self.name.data = instance.tags.get('Name', '')
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
    number_error_msg = _(u'Number of instances must be a whole number between 1-10')
    number_helptext = _(u'You cannot launch more than 10 instances in a single security group')
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
    vpc_network = wtforms.SelectField(label=_(u'VPC network'))
    vpc_network_helptext = _(u'Launch your instance into one of your Virtual Private Clouds')
    vpc_subnet = wtforms.SelectField(label=_(u'VPC subnet'))
    associate_public_ip_address = wtforms.SelectField(label=_(u'Auto-assign public IP'))
    associate_public_ip_address_helptext = _(u"Give your instance a non-persistent IP address \
        from the subnet\'s pool so it is accessible from the Internet. \
        If you want a persistent address, select Disabled and assign an elastic IP after launch.")
    keypair_error_msg = _(u'Key pair is required')
    keypair = wtforms.SelectField(
        label=_(u'Key name'),
        validators=[validators.InputRequired(message=keypair_error_msg)],
    )
    securitygroup_error_msg = _(u'Security group is required')
    securitygroup = wtforms.SelectMultipleField(
        label=_(u'Security group'),
        validators=[validators.InputRequired(message=securitygroup_error_msg)],
    )
    role = wtforms.SelectField()
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    userdata_file_helptext = _(u'User data file may not exceed 16 KB')
    userdata_file = wtforms.FileField(label='')
    kernel_id = wtforms.SelectField(label=_(u'Kernel ID'))
    ramdisk_id = wtforms.SelectField(label=_(u'RAM disk ID (RAMFS)'))
    monitoring_enabled = wtforms.BooleanField(label=_(u'Enable monitoring'))
    private_addressing = wtforms.BooleanField(label=_(u'Use private addressing only'))

    def __init__(self, request, image=None, securitygroups=None, conn=None, vpc_conn=None, iam_conn=None, **kwargs):
        super(LaunchInstanceForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.vpc_conn = vpc_conn
        self.iam_conn = iam_conn
        self.image = image
        self.securitygroups = securitygroups
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.set_error_messages()
        self.monitoring_enabled.data = True
        self.choices_manager = ChoicesManager(conn=conn)
        self.vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.set_help_text()
        self.set_choices(request)
        self.role.data = ''

        if image is not None:
            self.image_id.data = self.image.id
            self.kernel_id.data = image.kernel_id or ''
            self.ramdisk_id.data = image.ramdisk_id or ''

    def set_help_text(self):
        self.number.help_text = self.number_helptext
        self.vpc_network.label_help_text = self.vpc_network_helptext
        self.associate_public_ip_address.label_help_text = self.associate_public_ip_address_helptext
        self.userdata_file.help_text = self.userdata_file_helptext

    def set_choices(self, request):
        self.instance_type.choices = self.choices_manager.instance_types(cloud_type=self.cloud_type, add_blank=False)
        region = request.session.get('region')
        self.zone.choices = self.get_availability_zone_choices(region)
        self.vpc_network.choices = self.vpc_choices_manager.vpc_networks()
        self.vpc_subnet.choices = self.vpc_choices_manager.vpc_subnets()
        self.associate_public_ip_address.choices = self.get_associate_public_ip_address_choices()
        self.keypair.choices = self.get_keypair_choices()
        self.securitygroup.choices = self.choices_manager.security_groups(
            securitygroups=self.securitygroups, use_id=True, add_blank=False)
        self.role.choices = ChoicesManager(self.iam_conn).roles(add_blank=True)
        self.kernel_id.choices = self.choices_manager.kernels(image=self.image)
        self.ramdisk_id.choices = self.choices_manager.ramdisks(image=self.image)

        # Set default choices where applicable, defaulting to first non-blank choice
        if self.cloud_type == 'aws' and len(self.zone.choices) > 1:
            self.zone.data = self.zone.choices[1][0]
        # Set the defailt option to be the first choice
        if len(self.vpc_subnet.choices) > 1:
            self.vpc_subnet.data = self.vpc_subnet.choices[0][0]
        if len(self.vpc_network.choices) > 1:
            self.vpc_network.data = self.vpc_network.choices[0][0]

    def set_error_messages(self):
        self.number.error_msg = self.number_error_msg
        self.instance_type.error_msg = self.instance_type_error_msg
        self.keypair.error_msg = self.keypair_error_msg
        self.securitygroup.error_msg = self.securitygroup_error_msg

    def get_keypair_choices(self):
        choices = self.choices_manager.keypairs(add_blank=True, no_keypair_option=True)
        return choices

    def get_availability_zone_choices(self, region):
        choices = [('', _(u'No preference'))]
        choices.extend(self.choices_manager.availability_zones(region, add_blank=False))
        return choices

    def get_associate_public_ip_address_choices(self):
        choices = [('None', _(u'Enabled (use subnet setting)')), ('true', _(u'Enabled')), ('false', _(u'Disabled'))]
        return choices


class LaunchMoreInstancesForm(BaseSecureForm):
    """Form class for launch more instances like this one"""
    number_error_msg = _(u'Number of instances must be a whole number greater than 0')
    number = wtforms.IntegerField(
        label=_(u'How many instances would you like to launch?'),
        validators=[
            validators.InputRequired(message=number_error_msg),
            validators.NumberRange(min=1, max=10),  # Restrict num instances that can be launched in one go
        ],
    )
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    userdata_file_helptext = _(u'User data file may not exceed 16 KB')
    userdata_file = wtforms.FileField(label='')
    kernel_id = wtforms.SelectField(label=_(u'Kernel ID'))
    ramdisk_id = wtforms.SelectField(label=_(u'RAM disk ID (RAMFS)'))
    monitoring_enabled = wtforms.BooleanField(label=_(u'Enable detailed monitoring'))
    private_addressing = wtforms.BooleanField(label=_(u'Use private addressing only'))

    def __init__(self, request, image=None, instance=None, conn=None, **kwargs):
        super(LaunchMoreInstancesForm, self).__init__(request, **kwargs)
        self.image = image
        self.instance = instance
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
        self.monitoring_enabled.data = self.instance.monitored
        self.private_addressing.data = self.enable_private_addressing()
        self.number.data = 1

    def enable_private_addressing(self):
        if self.instance.private_ip_address == self.instance.ip_address:
            return True
        return False


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
        from ..views import BaseView
        choices = [('', _(u'select...'))]
        for volume in self.volumes:
            if self.instance and volume.zone == self.instance.placement and volume.attach_data.status is None:
                name_tag = volume.tags.get('Name')
                extra = ' ({name})'.format(name=name_tag) if name_tag else ''
                vol_name = '{id}{extra}'.format(id=volume.id, extra=extra)
                choices.append((volume.id, BaseView.escape_braces(vol_name)))
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
    key_name = wtforms.SelectMultipleField(label=_(u'Key pair'))
    security_group = wtforms.SelectMultipleField(label=_(u'Security group'))
    scaling_group = wtforms.SelectMultipleField(label=_(u'Scaling group'))
    tags = TextEscapedField(label=_(u'Tags'))
    roles = wtforms.SelectMultipleField(label=_(u'Roles'))
    vpc_id = wtforms.SelectMultipleField(label=_(u'VPC network'))
    subnet_id = wtforms.SelectMultipleField(label=_(u'VPC subnet'))

    def __init__(self, request, ec2_conn=None, autoscale_conn=None,
                 iam_conn=None, vpc_conn=None,
                 cloud_type='euca', **kwargs):
        super(InstancesFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.cloud_type = cloud_type
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        self.autoscale_choices_manager = ChoicesManager(conn=autoscale_conn)
        self.iam_choices_manager = ChoicesManager(conn=iam_conn)
        self.vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        region = request.session.get('region')
        self.availability_zone.choices = self.get_availability_zone_choices(region)
        self.state.choices = self.get_status_choices()
        self.instance_type.choices = self.get_instance_type_choices()
        self.root_device_type.choices = self.get_root_device_type_choices()
        self.key_name.choices = self.ec2_choices_manager.keypairs(
            add_blank=False, no_keypair_filter_option=True)
        self.security_group.choices = self.ec2_choices_manager.security_groups(add_blank=False)
        self.scaling_group.choices = self.autoscale_choices_manager.scaling_groups(add_blank=False)
        if cloud_type=='aws':
            del self.roles
        else:
            self.roles.choices = self.iam_choices_manager.roles(add_blank=False)
        self.vpc_id.choices = self.vpc_choices_manager.vpc_networks(add_blank=False)
        self.vpc_id.choices.append(('None', _(u'No VPC')))
        self.vpc_id.choices = sorted(self.vpc_id.choices)
        self.subnet_id.choices = self.vpc_choices_manager.vpc_subnets(add_blank=False)

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


class InstanceTypeForm(BaseSecureForm):
    """CSRF-protected form to disassociate IP from an instance"""
    pass


class InstanceCreateImageForm(BaseSecureForm):
    """CSRF-protected form to create an image from an instance"""
    name_error_msg = _(
        u"Name must be between 3 and 128 characters long, and may contain letters, numbers, "
        u"'(', ')', '.', '-', '/' and '_', and cannot contain spaces.")
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.InputRequired(message=name_error_msg)],
    )
    desc_error_msg = _(u'Description must be less than 255 characters')
    description = wtforms.TextAreaField(
        label=_(u'Description'),
        validators=[validators.Length(max=255, message=desc_error_msg)],
    )
    no_reboot = wtforms.BooleanField(label=_(u'No reboot'))
    s3_bucket = wtforms.SelectField(
        label=_(u'Bucket name'), validators=[validators.InputRequired(message=_(u'You must select a bucket to use.'))])
    s3_bucket_error_msg = _('Bucket name is required and may contain lowercase letters, numbers, hyphens, and/or dots.')
    s3_prefix = wtforms.TextField(
        label=_(u'Prefix'), validators=[validators.InputRequired(message=_(u'You must supply a prefix'))])
    s3_prefix_error_msg = _('Prefix is required and may contain lowercase letters, numbers, hyphens, and/or dots.')

    def __init__(self, request, s3_conn=None, **kwargs):
        super(InstanceCreateImageForm, self).__init__(request, **kwargs)
        self.s3_conn = s3_conn
        # Set choices
        self.choices_manager = ChoicesManager(conn=self.s3_conn)
        self.s3_bucket.choices = self.choices_manager.buckets()
        self.s3_bucket.error_msg = self.s3_bucket_error_msg
        self.s3_prefix.data = _(u'image')
        self.s3_prefix.error_msg = self.s3_prefix_error_msg
        # Set error msg
        self.name.error_msg = self.name_error_msg
        # Set help text
        no_reboot_helptext = _(
            u'When checked, the instance will not be shut down before the image is created. '
            u'May impact file integrity of the image.')
        self.no_reboot.label_help_text = no_reboot_helptext
        s3_bucket_helptext = _(u'Choose from your existing buckets, or enter a name to create a new bucket')
        self.s3_bucket.label_help_text = s3_bucket_helptext
        s3_prefix_helptext = _(u'The beginning of your image file name')
        self.s3_prefix.label_help_text = s3_prefix_helptext
