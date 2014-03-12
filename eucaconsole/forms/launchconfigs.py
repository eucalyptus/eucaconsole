# -*- coding: utf-8 -*-
"""
Forms for Launch Config 

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm, ChoicesManager


class LaunchConfigDeleteForm(BaseSecureForm):
    """LaunchConfig deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


class CreateLaunchConfigForm(BaseSecureForm):
    """Create Launch Configuration form"""
    image_id = wtforms.HiddenField(label=_(u'Image'))
    name_error_msg = _(u'Name is required')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.InputRequired(message=name_error_msg)],
    )
    instance_type_error_msg = _(u'Instance type is required')
    instance_type = wtforms.SelectField(
        label=_(u'Instance type'),
        validators=[validators.InputRequired(message=instance_type_error_msg)],
    )
    keypair = wtforms.SelectField(label=_(u'Key name'))
    securitygroup_error_msg = _(u'Security group is required')
    securitygroup = wtforms.SelectField(
        label=_(u'Security group'),
        validators=[validators.InputRequired(message=securitygroup_error_msg)],
    )
    userdata = wtforms.TextAreaField(label=_(u'User data'))
    userdata_file_helptext = _(u'User data file may not exceed 16 KB')
    userdata_file = wtforms.FileField(label=_(u''))
    kernel_id = wtforms.SelectField(label=_(u'Kernel ID'))
    ramdisk_id = wtforms.SelectField(label=_(u'RAM disk ID (RAMFS)'))
    monitoring_enabled = wtforms.BooleanField(label=_(u'Enable monitoring'))

    def __init__(self, request, image=None, securitygroups=None, conn=None, **kwargs):
        super(CreateLaunchConfigForm, self).__init__(request, **kwargs)
        self.image = image
        self.securitygroups = securitygroups
        self.conn = conn
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
        self.keypair.choices = self.choices_manager.keypairs(add_blank=False, no_keypair_option=True)
        self.securitygroup.choices = self.choices_manager.security_groups(
            securitygroups=self.securitygroups, add_blank=False)
        self.kernel_id.choices = self.choices_manager.kernels(image=self.image)
        self.ramdisk_id.choices = self.choices_manager.ramdisks(image=self.image)

        # Set default choices where applicable, defaulting to first non-blank choice
        if len(self.securitygroup.choices) > 1:
            self.securitygroup.data = 'default'
        if len(self.keypair.choices) > 1:
            self.keypair.data = self.keypair.choices[1][0]

    def set_error_messages(self):
        self.name.error_msg = self.name_error_msg
        self.instance_type.error_msg = self.instance_type_error_msg
        self.securitygroup.error_msg = self.securitygroup_error_msg

