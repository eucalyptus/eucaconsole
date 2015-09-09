# -*- coding: utf-8 -*-
# Copyright 2013-2015 Hewlett Packard Enterprise Development LP
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
Forms for Launch Config

"""
import wtforms
from wtforms import validators

from ..i18n import _
from . import BaseSecureForm, ChoicesManager


class LaunchConfigDeleteForm(BaseSecureForm):
    """LaunchConfig deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


class CreateLaunchConfigForm(BaseSecureForm):
    """Create Launch Configuration form"""
    image_id = wtforms.HiddenField(label=_(u'Image'))
    name_error_msg = _(u'Name must be between 1 and 255 characters long, and must not contain \'/\' and \'\\\'')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.InputRequired(message=name_error_msg)],
    )
    instance_type_error_msg = _(u'Instance type is required')
    instance_type = wtforms.SelectField(
        label=_(u'Instance type'),
        validators=[validators.InputRequired(message=instance_type_error_msg)],
    )
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
    associate_public_ip_address = wtforms.SelectField(label=_(u'VPC IP assignment'))
    associate_public_ip_address_helptext = _(u'This setting only applies \
        when this launch configuration is used with a scaling group using a VPC network.')
    role = wtforms.SelectField()
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    userdata_file_helptext = _(u'User data file may not exceed 16 KB')
    userdata_file = wtforms.FileField(label='')
    kernel_id = wtforms.SelectField(label=_(u'Kernel ID'))
    ramdisk_id = wtforms.SelectField(label=_(u'RAM disk ID (RAMFS)'))
    monitoring_enabled = wtforms.BooleanField(label=_(u'Enable monitoring'))
    create_sg_from_lc = wtforms.BooleanField(label=_(u'Create scaling group using this launch configuration'))

    def __init__(self, request, image=None, securitygroups=None, keyname=None, conn=None, iam_conn=None, **kwargs):
        super(CreateLaunchConfigForm, self).__init__(request, **kwargs)
        self.image = image
        self.keyname = keyname
        self.securitygroups = securitygroups
        self.conn = conn
        self.iam_conn = iam_conn
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.set_error_messages()
        self.monitoring_enabled.data = True
        self.create_sg_from_lc.data = True
        self.choices_manager = ChoicesManager(conn=conn)
        self.set_help_text()
        self.set_choices()
        self.set_monitoring_enabled_field()

        if image is not None:
            self.image_id.data = self.image.id
        if self.keyname is not None:
            self.keypair.data = self.keyname

    def set_monitoring_enabled_field(self):
        if self.cloud_type == 'euca':
            self.monitoring_enabled.data = True
            self.monitoring_enabled.help_text = _(u'Gather CloudWatch metric data for instances that use this launch configuration.')
        elif self.cloud_type == 'aws':
            self.monitoring_enabled.label.text = _(u'Enable detailed monitoring')
            self.monitoring_enabled.help_text = _(
                u'Gather all CloudWatch metric data at a higher frequency, '
                u'and enable data aggregation by AMI and instance type. '
                u'If left unchecked, data will still be gathered, but less often '
                u'and without aggregation. '
            )

    def set_help_text(self):
        self.associate_public_ip_address.help_text = self.associate_public_ip_address_helptext
        self.userdata_file.help_text = self.userdata_file_helptext

    def set_choices(self):
        self.instance_type.choices = self.choices_manager.instance_types(cloud_type=self.cloud_type)
        empty_key_opt = True
        if self.keyname is not None:
            empty_key_opt = False
        self.keypair.choices = self.choices_manager.keypairs(add_blank=empty_key_opt, no_keypair_option=True)
        self.securitygroup.choices = self.choices_manager.security_groups(
            securitygroups=self.securitygroups, use_id=True, add_blank=False)
        self.role.choices = ChoicesManager(self.iam_conn).roles(add_blank=True)
        self.kernel_id.choices = self.choices_manager.kernels(image=self.image)
        self.ramdisk_id.choices = self.choices_manager.ramdisks(image=self.image)
        self.associate_public_ip_address.choices = self.get_associate_public_ip_address_choices()

        # Set init data for security group
        if len(self.securitygroup.choices) > 1:
            self.securitygroup.data = [value for value, label in self.securitygroup.choices]

    @staticmethod
    def get_associate_public_ip_address_choices():
        return [
            ('None', _(u'Only for instances in default VPC & subnet')),
            ('true', _(u'For all instances')), ('false', _(u'Never'))
        ]

    def set_error_messages(self):
        self.name.error_msg = self.name_error_msg
        self.instance_type.error_msg = self.instance_type_error_msg
        self.securitygroup.error_msg = self.securitygroup_error_msg


class LaunchConfigsFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    availability_zone = wtforms.SelectMultipleField(label=_(u'Availability zone'))
    instance_type = wtforms.SelectMultipleField(label=_(u'Instance type'))
    root_device_type = wtforms.SelectMultipleField(label=_(u'Root device type'))
    key_name = wtforms.SelectMultipleField(label=_(u'Key pair'))
    security_groups = wtforms.SelectMultipleField(label=_(u'Security group'))
    scaling_group = wtforms.SelectMultipleField(label=_(u'Scaling group'))

    def __init__(self, request, cloud_type='euca', ec2_conn=None, autoscale_conn=None, **kwargs):
        super(LaunchConfigsFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.cloud_type = cloud_type
        self.ec2_conn = ec2_conn
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        self.autoscale_choices_manager = ChoicesManager(conn=autoscale_conn)
        region = request.session.get('region')
        self.availability_zone.choices = self.get_availability_zone_choices(region)
        self.instance_type.choices = self.ec2_choices_manager.instance_types(
            add_blank=False, cloud_type=self.cloud_type, add_description=False)
        self.root_device_type.choices = self.get_root_device_type_choices()
        self.key_name.choices = self.ec2_choices_manager.keypairs(add_blank=False, no_keypair_filter_option=True)
        self.security_groups.choices = self.ec2_choices_manager.security_groups(use_id=True, add_blank=False)
        self.scaling_group.choices = self.autoscale_choices_manager.scaling_groups(add_blank=False)
        self.facets = [
            {'name': 'availability_zone', 'label': self.availability_zone.label.text,
                'options': self.get_availability_zone_choices(region)},
            {'name': 'instance_type', 'label': self.instance_type.label.text,
                'options': self.get_options_from_choices(self.instance_type.choices)},
            {'name': 'root_device_type', 'label': self.root_device_type.label.text,
                'options': self.get_root_device_type_choices()},
            {'name': 'key_name', 'label': self.key_name.label.text,
                'options': self.get_options_from_choices(self.key_name.choices)},
            {'name': 'security_group', 'label': self.security_groups.label.text,
                'options': self.get_options_from_choices(self.security_groups.choices)},
            {'name': 'scaling_group', 'label': self.scaling_group.label.text,
                'options': self.get_options_from_choices(self.autoscale_choices_manager.scaling_groups(add_blank=False))},
        ]

    def get_availability_zone_choices(self, region):
        return self.get_options_from_choices(self.ec2_choices_manager.availability_zones(region, add_blank=False))

    @staticmethod
    def get_root_device_type_choices():
        return [
            {'key': 'ebs', 'label': _(u'EBS')},
            {'key': 'instance-store', 'label': _(u'Instance-store')}
        ]

