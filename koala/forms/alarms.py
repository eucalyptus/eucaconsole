# -*- coding: utf-8 -*-
"""
Forms for CloudWatch Alarms

"""
from collections import namedtuple
from operator import itemgetter

import wtforms
from wtforms import validators

from boto.ec2.cloudwatch.metric import Metric

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm, ChoicesManager, BLANK_CHOICE
from ..constants.cloudwatch import METRIC_TYPES


class CloudWatchAlarmCreateForm(BaseSecureForm):
    """Form for creating a CloudWatch alarm"""
    name_error_msg = _(u'Name is required')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[
            validators.InputRequired(message=name_error_msg),
        ],
    )
    desc_error_msg = _(u'Description is required')
    description = wtforms.TextAreaField(
        label=_(u'Description'),
        validators=[
            validators.Length(max=255, message=_(u'Description must be less than 255 characters'))
        ],
    )
    metric_error_msg = _(u'Metric is required')
    metric = wtforms.SelectField(
        label=_(u'Metric'),
        validators=[
            validators.InputRequired(message=metric_error_msg),
        ],
    )
    comparison_error_msg = _(u'Comparison is required')
    comparison = wtforms.SelectField(
        label=_(u'Comparison'),
        validators=[
            validators.InputRequired(message=comparison_error_msg),
        ],
    )
    statistic_error_msg = _(u'Statistic is required')
    statistic = wtforms.SelectField(
        label=_(u'Statistic'),
        validators=[
            validators.InputRequired(message=statistic_error_msg),
        ],
    )
    threshold_error_msg = _(u'Trigger threshold is required')
    threshold = wtforms.IntegerField(
        label=_(u'Trigger threshold'),
        validators=[
            validators.InputRequired(message=threshold_error_msg),
        ],
    )
    period_help_text = _(u'Length of measurement period in seconds.')
    period_error_msg = _(u'Period length is required')
    period = wtforms.IntegerField(
        label=_(u'Period length'),
        validators=[
            validators.InputRequired(message=period_error_msg),
        ],
    )
    evaluation_periods_help_text = _(
        u'How many consecutive periods the trigger threshold must be breached before the alarm is triggered.')
    evaluation_periods_error_msg = _(u'Measurement periods is required')
    evaluation_periods = wtforms.IntegerField(
        label=_(u'Measurement periods'),
        validators=[
            validators.InputRequired(message=evaluation_periods_error_msg),
        ],
    )
    unit_error_msg = _(u'Unit is required')
    unit = wtforms.SelectField(
        label=_(u'Unit'),
        validators=[
            validators.InputRequired(message=unit_error_msg),
        ],
    )
    availability_zone = wtforms.SelectField()
    image_id = wtforms.SelectField()
    instance_id = wtforms.SelectField()
    instance_type = wtforms.SelectField()
    load_balancer_name = wtforms.SelectField()
    scaling_group_name = wtforms.SelectField()
    volume_id = wtforms.SelectField()

    def __init__(self, request, ec2_conn=None, autoscale_conn=None, elb_conn=None, metrics=None,
                 scaling_group=None, **kwargs):
        super(CloudWatchAlarmCreateForm, self).__init__(request, **kwargs)
        self.elb_conn = ec2_conn
        self.autoscale_conn = autoscale_conn
        self.elb_conn = elb_conn
        self.metrics = metrics or []
        self.scaling_group = scaling_group
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.choices_from_metrics = self.get_choices_from_metrics()
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        self.autoscale_choices_manager = ChoicesManager(conn=autoscale_conn)
        self.elb_choices_manager = ChoicesManager(conn=elb_conn)
        self.set_initial_data()
        self.set_error_messages()
        self.set_choices()
        self.set_help_text()

    def set_initial_data(self):
        self.evaluation_periods.data = 1
        self.period.data = 120

        if self.scaling_group is not None:
            self.scaling_group_name.data = self.scaling_group.name

    def set_choices(self):
        self.comparison.choices = self.get_comparison_choices()
        self.statistic.choices = self.get_statistic_choices()
        self.metric.choices = self.get_metric_choices()
        self.unit.choices = self.get_unit_choices()
        self.availability_zone.choices = self.ec2_choices_manager.availability_zones()
        self.image_id.choices = self.choices_from_metrics.image_choices
        self.instance_id.choices = self.choices_from_metrics.instance_choices
        self.instance_type.choices = self.get_instance_type_choices()
        self.load_balancer_name.choices = self.elb_choices_manager.load_balancers()
        self.scaling_group_name.choices = self.autoscale_choices_manager.scaling_groups()
        self.volume_id.choices = self.choices_from_metrics.volume_choices

    def set_help_text(self):
        self.evaluation_periods.help_text = self.evaluation_periods_help_text
        self.period.help_text = self.period_help_text

    def set_error_messages(self):
        self.name.error_msg = self.name_error_msg
        self.description.error_msg = self.desc_error_msg
        self.comparison.error_msg = self.comparison_error_msg
        self.statistic.error_msg = self.statistic_error_msg
        self.metric.error_msg = self.metric_error_msg
        self.threshold.error_msg = self.threshold_error_msg
        self.period.error_msg = self.period_error_msg
        self.evaluation_periods.error_msg = self.evaluation_periods_error_msg
        self.unit.error_msg = self.unit_error_msg

    def get_instance_type_choices(self):
        return self.ec2_choices_manager.instance_types(cloud_type=self.cloud_type)

    def get_choices_from_metrics(self):
        Choices = namedtuple('Choices', ['image_choices', 'instance_choices', 'volume_choices'])
        image_choices = []
        instance_choices = []
        volume_choices = []
        for metric in self.metrics:
            if hasattr(metric, 'dimensions'):
                if metric.dimensions.get('ImageId'):
                    image_id = metric.dimensions.get('ImageId')[0]
                    image_choices.append((image_id, image_id))
                elif metric.dimensions.get('InstanceId'):
                    instance_id = metric.dimensions.get('InstanceId')[0]
                    instance_choices.append((instance_id, instance_id))
                elif metric.dimensions.get('VolumeId'):
                    volume_id = metric.dimensions.get('VolumeId')[0]
                    volume_choices.append((volume_id, volume_id))
        return Choices(
            image_choices=sorted(set(image_choices)),
            instance_choices=sorted(set(instance_choices)),
            volume_choices=sorted(set(volume_choices))
        )

    @staticmethod
    def get_metric_choices():
        choices = [BLANK_CHOICE]
        for metric in METRIC_TYPES:
            value = metric.get('name')
            label = '{0} - {1}'.format(metric.get('namespace'), metric.get('name'))
            choices.append((value, label))
        return sorted(set(choices), key=itemgetter(1))

    @staticmethod
    def get_comparison_choices():
        return (
            ('>=', '>='), ('>', '>'), ('<=', '<='), ('<', '<')
        )

    @staticmethod
    def get_statistic_choices():
        return sorted([(choice, choice) for choice in Metric.Statistics])

    @staticmethod
    def get_unit_choices():
        return [(choice, choice) for choice in Metric.Units if choice is not None]


class CloudWatchAlarmDeleteForm(BaseSecureForm):
    """CloudWatch Alarm deletion form"""
    pass

