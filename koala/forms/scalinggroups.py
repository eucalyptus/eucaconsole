# -*- coding: utf-8 -*-
"""
Forms for Scaling Group 

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class ScalingGroupEditForm(BaseSecureForm):
    """Edit Scaling Group form"""
    launch_config_error_msg = _(u'Launch configuration is required')
    launch_config = wtforms.SelectField(
        label=_(u'Launch configuration'),
        validators=[
            validators.Required(message=launch_config_error_msg),
        ],
    )
    desired_capacity_error_msg = _(u'Desired capacity is required')
    desired_capacity = wtforms.IntegerField(
        label=_(u'Desired capacity'),
        validators=[
            validators.Required(message=desired_capacity_error_msg),
            validators.NumberRange(min=0, max=99),
        ],
    )
    max_size_error_msg = _(u'Max size is required')
    max_size = wtforms.IntegerField(
        label=_(u'Max size'),
        validators=[
            validators.Required(message=max_size_error_msg),
            validators.NumberRange(min=0, max=99),
        ],
    )
    min_size_error_msg = _(u'Min size is required')
    min_size = wtforms.IntegerField(
        label=_(u'Min size'),
        validators=[
            validators.Required(message=min_size_error_msg),
            validators.NumberRange(min=0, max=99),
        ],
    )

    def __init__(self, request, scaling_group=None, conn=None, launch_configs=None, **kwargs):
        super(ScalingGroupEditForm, self).__init__(request, **kwargs)
        self.scaling_group = scaling_group
        self.conn = conn
        self.launch_configs = launch_configs
        self.set_error_messages()
        self.set_choices()

        if scaling_group is not None:
            self.launch_config.data = scaling_group.launch_config_name
            self.desired_capacity.data = scaling_group.desired_capacity
            self.max_size.data = scaling_group.max_size
            self.min_size.data = scaling_group.min_size or 0

    def set_choices(self):
        self.launch_config.choices = self.get_launch_config_choices()

    def set_error_messages(self):
        self.launch_config.error_msg = self.launch_config_error_msg
        self.desired_capacity.error_msg = self.desired_capacity_error_msg
        self.max_size.error_msg = self.max_size_error_msg
        self.min_size.error_msg = self.min_size_error_msg

    def get_launch_config_choices(self):
        choices = []
        launch_configs = self.launch_configs
        if launch_configs is None:
            launch_configs = self.conn.get_all_launch_configurations()
        for launch_config in launch_configs:
            choices.append((launch_config.name, launch_config.name))
        if self.scaling_group:
            launch_config_name = self.scaling_group.launch_config_name
            choices.append((launch_config_name, launch_config_name))
        return sorted(set(choices))


class ScalingGroupDeleteForm(BaseSecureForm):
    """ScalingGroup deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


