# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS CloudWatch alarms

"""
from boto.ec2.cloudwatch import MetricAlarm
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.response import Response
from pyramid.view import view_config

from ..forms.alarms import CloudWatchAlarmCreateForm, CloudWatchAlarmDeleteForm
from ..models import Notification
from ..views import LandingPageView, BaseView


class CloudWatchAlarmsView(LandingPageView):
    """CloudWatch Alarms landing page view"""
    TEMPLATE = '../templates/cloudwatch/alarms.pt'

    def __init__(self, request):
        super(CloudWatchAlarmsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/cloudwatch/alarms'
        self.cloudwatch_conn = self.get_connection(conn_type='cloudwatch')
        self.metrics = self.cloudwatch_conn.list_metrics()
        self.create_form = CloudWatchAlarmCreateForm(
            self.request, metrics=self.metrics, formdata=self.request.params or None)
        self.delete_form = CloudWatchAlarmDeleteForm(self.request, formdata=self.request.params or None)
        self.filter_keys = []
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name')),
        ]
        self.render_dict = dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.request.route_url('cloudwatch_alarms_json'),
        )

    @view_config(route_name='cloudwatch_alarms', renderer=TEMPLATE, request_method='GET')
    def alarms_landing(self):
        return self.render_dict

    @view_config(route_name='cloudwatch_alarms_create', renderer=TEMPLATE, request_method='POST')
    def cloudwatch_alarms_create(self):
        location = self.request.route_url('cloudwatch_alarms')
        if self.create_form.validate():
            try:
                metric_name = self.request.params.get('metric')
                metric = self.cloudwatch_conn.list_metrics(metric_name=metric_name)[0]
                name = self.request.params.get('name')
                comparison = self.request.params.get('comparison')
                threshold = self.request.params.get('threshold')
                period = self.request.params.get('period')
                evaluation_periods = self.request.params.get('evaluation_periods')
                statistic = self.request.params.get('statistic')
                alarm = MetricAlarm(
                    name, comparison, threshold, period, evaluation_periods, statistic,
                    description=self.request.params.get('description'),
                )
                alarm.metric = metric
                self.cloudwatch_conn.put_metric_alarm(alarm)
                prefix = _(u'Successfully created alarm')
                msg = '{0} {1}'.format(prefix, alarm.name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='cloudwatch_alarms_delete', renderer=TEMPLATE, request_method='POST')
    def cloudwatch_alarms_delete(self):
        if self.delete_form.validate():
            location = self.request.route_url('cloudwatch_alarms')
            alarm_name = self.request.params.get('name')
            try:
                self.cloudwatch_conn.delete_alarm(alarm_name)
                prefix = _(u'Successfully deleted alarm')
                msg = '{0} {1}'.format(prefix, alarm_name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict


class CloudWatchAlarmsJsonView(BaseView):
    """JSON response for CloudWatch Alarms landing page et. al."""
    @view_config(route_name='cloudwatch_alarms_json', renderer='json', request_method='GET')
    def cloudwatch_alarms_json(self):
        alarms = []
        try:
            items = self.get_items()
        except BotoServerError as err:
            return Response(status=err.status, body=err.message)
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

