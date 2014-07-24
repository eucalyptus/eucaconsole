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
Forms for CloudWatch Alarms

"""
from operator import itemgetter

import wtforms
from wtforms import validators

from boto.ec2.cloudwatch.metric import Metric

from ..constants.cloudwatch import METRIC_TYPES
from ..i18n import _
from . import BaseSecureForm, ChoicesManager, BLANK_CHOICE


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
    threshold_error_msg = _(u'Trigger threshold amount is required')
    threshold = wtforms.IntegerField(
        label=_(u'Trigger threshold'),
        validators=[
            validators.InputRequired(message=threshold_error_msg),
        ],
    )
    period_help_text = _(u'Length of measurement period in minutes.')
    period_error_msg = _(u'Period length is required and must be a whole number greater than zero')
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
        label=_(u'Periods'),
        validators=[
            validators.InputRequired(message=evaluation_periods_error_msg),
        ],
    )
    unit = wtforms.SelectField(label=_(u'Unit'))
    image_id = wtforms.TextField(label=_(u'Image'))
    availability_zone = wtforms.SelectField()
    instance_id = wtforms.SelectField()
    instance_type = wtforms.SelectField()
    load_balancer_name = wtforms.SelectField()
    scaling_group_name = wtforms.SelectField()
    volume_id = wtforms.SelectField()

    def __init__(self, request, ec2_conn=None, autoscale_conn=None, elb_conn=None, scaling_group=None, **kwargs):
        super(CloudWatchAlarmCreateForm, self).__init__(request, **kwargs)
        self.ec2_conn = ec2_conn
        self.autoscale_conn = autoscale_conn
        self.elb_conn = elb_conn
        self.scaling_group = scaling_group
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        self.autoscale_choices_manager = ChoicesManager(conn=autoscale_conn)
        self.elb_choices_manager = ChoicesManager(conn=elb_conn)
        self.set_initial_data()
        self.set_error_messages()
        region = request.session.get('region')
        self.set_choices(region)
        self.set_help_text()

    def set_initial_data(self):
        self.evaluation_periods.data = 1
        self.period.data = 5

        if self.scaling_group is not None:
            self.scaling_group_name.data = self.scaling_group.name
            self.statistic.data = 'SampleCount'
            self.metric.data = 'GroupDesiredCapacity'
            self.unit.data = 'Count'

    def set_choices(self, region):
        self.comparison.choices = self.get_comparison_choices()
        self.statistic.choices = self.get_statistic_choices()
        self.metric.choices = self.get_metric_choices()
        self.unit.choices = self.get_unit_choices()
        self.availability_zone.choices = self.ec2_choices_manager.availability_zones(region)
        self.instance_id.choices = self.ec2_choices_manager.instances()
        self.instance_type.choices = self.get_instance_type_choices()
        self.load_balancer_name.choices = self.elb_choices_manager.load_balancers()
        self.scaling_group_name.choices = self.autoscale_choices_manager.scaling_groups()
        self.volume_id.choices = self.ec2_choices_manager.volumes()

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

    def get_instance_type_choices(self):
        return self.ec2_choices_manager.instance_types(cloud_type=self.cloud_type)

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
        choices = [BLANK_CHOICE]
        for choice in Metric.Units:
            if choice is not None:
                choices.append((choice, choice))
        return choices


class CloudWatchAlarmDeleteForm(BaseSecureForm):
    """CloudWatch Alarm deletion form"""
    pass

