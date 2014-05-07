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
Pyramid views for Eucalyptus and AWS CloudWatch alarms

"""
import simplejson as json

from boto.ec2.cloudwatch import MetricAlarm

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..constants.cloudwatch import METRIC_DIMENSION_NAMES, METRIC_DIMENSION_INPUTS
from ..forms.alarms import CloudWatchAlarmCreateForm, CloudWatchAlarmDeleteForm
from ..models import Notification
from ..views import LandingPageView, BaseView, JSONResponse
from . import boto_error_handler


class CloudWatchAlarmsView(LandingPageView):
    """CloudWatch Alarms landing page view"""
    TEMPLATE = '../templates/cloudwatch/alarms.pt'

    def __init__(self, request):
        super(CloudWatchAlarmsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/cloudwatch/alarms'
        self.cloudwatch_conn = self.get_connection(conn_type='cloudwatch')
        self.ec2_conn = self.get_connection()
        self.elb_conn = self.get_connection(conn_type='elb')
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        # TODO: not likely to fail, but if session creds expire?
        self.create_form = CloudWatchAlarmCreateForm(
            self.request, ec2_conn=self.ec2_conn, elb_conn=self.elb_conn, autoscale_conn=self.autoscale_conn,
            formdata=self.request.params or None)
        self.delete_form = CloudWatchAlarmDeleteForm(self.request, formdata=self.request.params or None)
        self.filter_keys = ['name']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name')),
        ]
        self.render_dict = dict(
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.request.route_path('cloudwatch_alarms_json'),
        )

    @view_config(route_name='cloudwatch_alarms', renderer=TEMPLATE, request_method='GET')
    def alarms_landing(self):
        return self.render_dict

    @view_config(route_name='cloudwatch_alarms_create', renderer=TEMPLATE, request_method='POST')
    def cloudwatch_alarms_create(self):
        location = self.request.route_path('cloudwatch_alarms')
        redirect_location = self.request.params.get('redirect_location')
        if redirect_location:
            location = self.sanitize_url(redirect_location)
        if self.create_form.validate():
            with boto_error_handler(self.request, location):
                metric = self.request.params.get('metric')
                name = self.request.params.get('name')
                namespace = self.request.params.get('namespace')
                statistic = self.request.params.get('statistic')
                comparison = self.request.params.get('comparison')
                threshold = self.request.params.get('threshold')
                period = self.request.params.get('period')
                evaluation_periods = self.request.params.get('evaluation_periods')
                unit = self.request.params.get('unit')
                description = self.request.params.get('description', '')
                dimension_param = self.request.params.get('dimension')
                dimension = self.get_dimension_name(dimension_param)
                dimension_value = self.get_dimension_value(dimension_param)
                dimensions = {dimension: dimension_value}
                self.log_request(_(u"Creating alarm {0}").format(name))
                alarm = MetricAlarm(
                    name=name, metric=metric, namespace=namespace, statistic=statistic, comparison=comparison,
                    threshold=threshold, period=period, evaluation_periods=evaluation_periods, unit=unit,
                    description=description, dimensions=dimensions
                )
                self.cloudwatch_conn.put_metric_alarm(alarm)
                prefix = _(u'Successfully created alarm')
                msg = '{0} {1}'.format(prefix, alarm.name)
            if self.request.is_xhr:
                resp = JSONResponse()
                resp.body = json.dumps(dict(new_alarm=name))
                return resp
            else:
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                return HTTPFound(location=location)
        else:
            error_msg_list = self.create_form.get_errors_list()
            if self.request.is_xhr:
                return JSONResponse(status=400, message=', '.join(error_msg_list))
            self.request.error_messages = error_msg_list
        return self.render_dict

    @view_config(route_name='cloudwatch_alarms_delete', renderer=TEMPLATE, request_method='POST')
    def cloudwatch_alarms_delete(self):
        if self.delete_form.validate():
            location = self.request.route_path('cloudwatch_alarms')
            alarm_name = self.request.params.get('name')
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Deleting alarm {0}").format(alarm_name))
                self.cloudwatch_conn.delete_alarm(alarm_name)
                prefix = _(u'Successfully deleted alarm')
                msg = '{0} {1}'.format(prefix, alarm_name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    def get_dimension_value(self, key=None):
        input_field = METRIC_DIMENSION_INPUTS.get(key)
        return [self.request.params.get(input_field)]

    @staticmethod
    def get_dimension_name(key=None):
        return METRIC_DIMENSION_NAMES.get(key)


class CloudWatchAlarmsJsonView(BaseView):
    """JSON response for CloudWatch Alarms landing page et. al."""
    @view_config(route_name='cloudwatch_alarms_json', renderer='json', request_method='GET')
    def cloudwatch_alarms_json(self):
        with boto_error_handler(self.request):
            items = self.get_items()
            alarms = []
            for alarm in items:
                alarms.append(dict(
                    name=alarm.name,
                    statistic=alarm.statistic,
                    metric=alarm.metric,
                    period=alarm.period,
                    comparison=alarm.comparison,
                    threshold=alarm.threshold,
                    unit=alarm.unit,
                ))
            return dict(results=alarms)

    def get_items(self):
        conn = self.get_connection(conn_type='cloudwatch')
        return conn.describe_alarms() if conn else []

