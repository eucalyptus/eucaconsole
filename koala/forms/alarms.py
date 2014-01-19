# -*- coding: utf-8 -*-
"""
Forms for CloudWatch Alarms

"""
import wtforms
from wtforms import validators

from boto.ec2.cloudwatch.metric import Metric

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


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

    def __init__(self, request, metrics=None, **kwargs):
        super(CloudWatchAlarmCreateForm, self).__init__(request, **kwargs)
        self.metrics = metrics or []
        self.set_initial_data()
        self.set_error_messages()
        self.set_choices()
        self.set_help_text()

    def set_initial_data(self):
        self.evaluation_periods.data = 1
        self.period.data = 120

    def set_choices(self):
        self.comparison.choices = self.get_comparison_choices()
        self.statistic.choices = self.get_statistic_choices()
        self.metric.choices = self.get_metric_choices()
        self.unit.choices = self.get_unit_choices()

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

    def get_metric_choices(self):
        choices = []
        for metric in self.metrics:
            choices.append((metric.name, metric.name))
        return sorted(set(choices))

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

