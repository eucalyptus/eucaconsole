# -*- coding: utf-8 -*-
"""
Forms for Scaling Group 

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm, ChoicesManager


class BaseScalingGroupForm(BaseSecureForm):
    """Base class for Create/Edit Scaling Group forms"""
    launch_config_error_msg = _(u'Launch configuration is required')
    launch_config = wtforms.SelectField(
        label=_(u'Launch configuration'),
        validators=[
            validators.InputRequired(message=launch_config_error_msg),
        ],
    )
    availability_zones_error_msg = _(u'At least one availability zone is required')
    availability_zones = wtforms.SelectMultipleField(
        label=_(u'Availability zones'),
        validators=[
            validators.InputRequired(message=availability_zones_error_msg),
        ],
    )
    load_balancers = wtforms.SelectMultipleField(
        label=_(u'Load balancers'),
    )
    desired_capacity_error_msg = _(u'Field is required')
    desired_capacity = wtforms.IntegerField(
        label=_(u'Desired'),
        validators=[
            validators.InputRequired(message=desired_capacity_error_msg),
            validators.NumberRange(min=0, max=99),
        ],
    )
    max_size_error_msg = _(u'Max is required')
    max_size = wtforms.IntegerField(
        label=_(u'Max'),
        validators=[
            validators.InputRequired(message=max_size_error_msg),
            validators.NumberRange(min=0, max=99),
        ],
    )
    min_size_error_msg = _(u'Min is required')
    min_size = wtforms.IntegerField(
        label=_(u'Min'),
        validators=[
            validators.InputRequired(message=min_size_error_msg),
            validators.NumberRange(min=0, max=99),
        ],
    )
    health_check_type_error_msg = _(u'Health check type is required')
    health_check_type = wtforms.SelectField(
        label=_(u'Type'),
        validators=[
            validators.InputRequired(message=health_check_type_error_msg),
        ],
    )
    health_check_period_error_msg = _(u'Health check grace period is required')
    health_check_period_help_text = _(
        u'Length of time in seconds after a new EC2 instance comes into service that '
        u'Auto Scaling starts checking its health'
    )
    health_check_period = wtforms.IntegerField(
        label=_(u'Grace period (seconds)'),
        validators=[
            validators.InputRequired(message=health_check_period_error_msg),
        ],
    )

    def __init__(self, request, scaling_group=None, launch_configs=None,
                 autoscale_conn=None, ec2_conn=None, elb_conn=None, **kwargs):
        super(BaseScalingGroupForm, self).__init__(request, **kwargs)
        self.scaling_group = scaling_group
        self.launch_configs = launch_configs
        self.autoscale_conn = autoscale_conn
        self.ec2_conn = ec2_conn
        self.elb_conn = elb_conn

        # Set choices
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        self.elb_choices_manager = ChoicesManager(conn=elb_conn) if elb_conn else None
        self.launch_config.choices = self.get_launch_config_choices()
        self.health_check_type.choices = self.get_healthcheck_type_choices()
        self.availability_zones.choices = self.get_availability_zone_choices()
        self.load_balancers.choices = self.get_load_balancer_choices()

        # Set error messages
        self.launch_config.error_msg = self.launch_config_error_msg
        self.availability_zones.error_msg = self.availability_zones_error_msg
        self.desired_capacity.error_msg = self.desired_capacity_error_msg
        self.max_size.error_msg = self.max_size_error_msg
        self.min_size.error_msg = self.min_size_error_msg
        self.health_check_type.error_msg = self.health_check_type_error_msg
        self.health_check_period.error_msg = self.health_check_period_error_msg

        if scaling_group is not None:
            self.launch_config.data = scaling_group.launch_config_name
            self.availability_zones.data = scaling_group.availability_zones
            self.desired_capacity.data = int(scaling_group.desired_capacity) if scaling_group.desired_capacity else 1
            self.max_size.data = int(scaling_group.max_size) if scaling_group.max_size else 1
            self.min_size.data = int(scaling_group.min_size) if scaling_group.min_size else 0
            self.health_check_type.data = scaling_group.health_check_type
            self.health_check_period.data = scaling_group.health_check_period

    def get_launch_config_choices(self):
        choices = [('', _(u'Select a launch configuration...'))]
        launch_configs = self.launch_configs
        if launch_configs is None and self.autoscale_conn is not None:
            launch_configs = self.autoscale_conn.get_all_launch_configurations()
        for launch_config in launch_configs:
            choices.append((launch_config.name, launch_config.name))
        if self.scaling_group:
            launch_config_name = self.scaling_group.launch_config_name
            choices.append((launch_config_name, launch_config_name))
        return sorted(set(choices))

    def get_availability_zone_choices(self):
        return self.ec2_choices_manager.availability_zones(add_blank=False)

    def get_load_balancer_choices(self):
        choices = []
        if self.elb_choices_manager is not None:
            choices.extend(self.elb_choices_manager.load_balancers())
        if self.scaling_group and self.scaling_group.load_balancers:
            for load_balancer_name in self.scaling_group.load_balancers:
                choices.append((load_balancer_name, load_balancer_name))
        return sorted(set(choices))

    @staticmethod
    def get_healthcheck_type_choices():
        return [(u'EC2', u'EC2'), (u'ELB', _(u'Load Balancer'))]

    @staticmethod
    def get_termination_policy_choices():
        return (
            (u'Default', _(u'Default')),
            (u'OldestInstance', _(u'Oldest instance')),
            (u'NewestInstance', _(u'Newest instance')),
            (u'OldestLaunchConfiguration', _(u'Oldest launch configuration')),
            (u'ClosestToNextInstanceHour', _(u'Closest to next instance hour')),
        )


class ScalingGroupCreateForm(BaseScalingGroupForm):
    """Create Scaling Group form"""
    name_error_msg = _(u'Name is required')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[
            validators.InputRequired(message=name_error_msg),
        ],
    )

    def __init__(self, request, scaling_group=None, autoscale_conn=None, ec2_conn=None, launch_configs=None, **kwargs):
        super(ScalingGroupCreateForm, self).__init__(
            request, scaling_group=scaling_group, autoscale_conn=autoscale_conn,
            ec2_conn=ec2_conn, launch_configs=launch_configs, **kwargs)

        # Set error messages
        self.name.error_msg = self.name_error_msg

        # Set initial data
        self.availability_zones.data = [value for value, label in self.availability_zones.choices]


class ScalingGroupEditForm(BaseScalingGroupForm):
    """Edit Scaling Group form"""
    default_cooldown_error_msg = _(u'Default cooldown period is required')
    default_cooldown_help_text = _(
        u'Number of seconds after a Scaling Activity completes before any further scaling activities can start')
    default_cooldown = wtforms.IntegerField(
        label=_(u'Default cooldown period (seconds)'),
        validators=[
            validators.InputRequired(message=default_cooldown_error_msg),
        ],
    )
    termination_policies_error_msg = _(u'At least one termination policy is required')
    termination_policies_help_text = _(u'Add termination policies in the order they should be executed.')
    termination_policies = wtforms.SelectMultipleField(
        label=_(u'Termination policies'),
        validators=[
            validators.InputRequired(message=termination_policies_error_msg),
        ],
    )

    def __init__(self, request, scaling_group=None, autoscale_conn=None, ec2_conn=None, launch_configs=None, **kwargs):
        super(ScalingGroupEditForm, self).__init__(
            request, scaling_group=scaling_group, autoscale_conn=autoscale_conn,
            ec2_conn=ec2_conn, launch_configs=launch_configs, **kwargs)

        # Set choices
        self.termination_policies.choices = self.get_termination_policy_choices()

        # Set error messages
        self.default_cooldown.error_msg = self.default_cooldown_error_msg
        self.termination_policies.error_msg = self.termination_policies_error_msg

        # Set help text
        self.default_cooldown.help_text = self.default_cooldown_help_text
        self.health_check_period.help_text = self.health_check_period_help_text
        self.termination_policies.help_text = self.termination_policies_help_text

        if scaling_group is not None:
            self.default_cooldown.data = scaling_group.default_cooldown
            self.termination_policies.data = scaling_group.termination_policies


class ScalingGroupDeleteForm(BaseSecureForm):
    """Scaling Group deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


class ScalingGroupPolicyCreateForm(BaseSecureForm):
    """Form for creating a scaling group policy"""
    name_error_msg = _(u'Name is required')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[
            validators.InputRequired(message=name_error_msg),
        ],
    )
    adjustment_direction_error_msg = _(u'Action is required')
    adjustment_direction = wtforms.SelectField(
        label=_(u'Action'),
        validators=[
            validators.InputRequired(message=adjustment_direction_error_msg),
        ],
    )
    adjustment_amount_error_msg = _(u'Amount is required')
    adjustment_amount = wtforms.IntegerField(
        label=_(u'Amount'),
        validators=[
            validators.InputRequired(message=adjustment_amount_error_msg),
        ],
    )
    adjustment_type_error_msg = _(u'Measure is required')
    adjustment_type = wtforms.SelectField(
        label=_(u'Measure'),
        validators=[
            validators.InputRequired(message=adjustment_type_error_msg),
        ],
    )
    cooldown_error_msg = _(u'Cooldown period is required')
    cooldown_help_text = _(
        u'Time (in seconds) before Alarm related Scaling Activities can start after the previous Scaling Activity ends.'
    )
    cooldown = wtforms.IntegerField(
        label=_(u'Cooldown period (seconds)'),
        validators=[
            validators.InputRequired(message=cooldown_error_msg),
        ],
    )
    alarm_error_msg = _(u'Alarm is required')
    alarm = wtforms.SelectField(
        label=_(u'Alarm'),
        validators=[
            validators.InputRequired(message=alarm_error_msg),
        ],
    )

    def __init__(self, request, scaling_group=None, alarms=None, **kwargs):
        super(ScalingGroupPolicyCreateForm, self).__init__(request, **kwargs)
        self.scaling_group = scaling_group
        self.alarms = alarms or []
        self.set_error_messages()
        self.set_choices()
        self.set_help_text()

        if scaling_group is not None:
            self.adjustment_amount.data = 1
            self.cooldown.data = scaling_group.default_cooldown

    def set_choices(self):
        self.adjustment_direction.choices = self.get_adjustment_direction_choices()
        self.adjustment_type.choices = self.get_adjustment_type_choices()
        self.alarm.choices = self.get_alarm_choices()

    def set_error_messages(self):
        self.name.error_msg = self.name_error_msg
        self.adjustment_type.error_msg = self.adjustment_type_error_msg
        self.cooldown.error_msg = self.cooldown_error_msg
        self.alarm.error_msg = self.alarm_error_msg

    def set_help_text(self):
        self.cooldown.help_text = self.cooldown_help_text

    def get_alarm_choices(self):
        choices = []
        for alarm in self.alarms:
            choices.append((alarm.name, alarm.name))
        if len(choices) == 0:
            choices = [('', _(u'No alarms are available.'))]
        return sorted(choices)

    @staticmethod
    def get_adjustment_direction_choices():
        return (
            (u'up', _(u'Scale up by')),
            (u'down', _(u'Scale down by')),
        )

    @staticmethod
    def get_adjustment_type_choices():
        return (
            (u'ChangeInCapacity', _(u'Instance(s)')),
            (u'PercentChangeInCapacity', _(u'Percentage')),
        )


class ScalingGroupPolicyDeleteForm(BaseSecureForm):
    """Scaling Group policy deletion form"""
    pass


class ScalingGroupInstancesMarkUnhealthyForm(BaseSecureForm):
    """Scaling Group instance mark unhealthy form"""
    respect_grace_period = wtforms.BooleanField(label=_(u'Respect grace period?'))


class ScalingGroupInstancesTerminateForm(BaseSecureForm):
    """Scaling Group instance terminate form"""
    decrement_capacity = wtforms.BooleanField(label=_(u'Decrement capacity of scaling group?'))

