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
Pyramid views for Eucalyptus and AWS CloudWatch alarms

"""
import re
import simplejson as json

from boto.ec2.cloudwatch import MetricAlarm

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from ..constants.cloudwatch import (
    METRIC_DIMENSION_NAMES, METRIC_DIMENSION_INPUTS, METRIC_TYPES, METRIC_TITLE_MAPPING)

from ..forms.alarms import CloudWatchAlarmCreateForm, CloudWatchAlarmUpdateForm
from ..i18n import _
from ..models import Notification
from ..models.alarms import Alarm
from ..models.arn import AmazonResourceName
from ..views import LandingPageView, BaseView, JSONResponse
from . import boto_error_handler


class CloudWatchAlarmsView(LandingPageView):
    """CloudWatch Alarms landing page view"""
    TEMPLATE = '../templates/cloudwatch/alarms.pt'

    comparison_operators = {
        '>': 'GreaterThanThreshold',
        '<': 'LessThanThreshold',
        '>=': 'GreaterThanOrEqualToThreshold',
        '<=': 'LessThanOrEqualToThreshold'
    }

    def __init__(self, request):
        super(CloudWatchAlarmsView, self).__init__(request)
        self.title_parts = [_(u'Alarms')]
        self.initial_sort_key = 'name'
        self.prefix = '/alarms'
        self.cloudwatch_conn = self.get_connection(conn_type='cloudwatch')
        self.ec2_conn = self.get_connection()
        self.elb_conn = self.get_connection(conn_type='elb')
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        # TODO: not likely to fail, but if session creds expire?
        self.create_form = CloudWatchAlarmCreateForm(
            self.request, ec2_conn=self.ec2_conn, elb_conn=self.elb_conn, autoscale_conn=self.autoscale_conn,
            formdata=self.request.params or None)
        self.filter_keys = ['name']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='state', name=_(u'State')),
            dict(key='name', name=_(u'Name')),
            dict(key='metric', name=_(u'Metric')),
        ]
        self.render_dict = dict(
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.request.route_path('cloudwatch_alarms_json'),
            search_facets=[],
            alarm_form=self.create_form,
            metric_unit_mapping=self.get_metric_unit_mapping(),
            create_alarm_redirect=self.request.route_path('cloudwatch_alarms'),
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
                # Convert to seconds
                period = int(self.request.params.get('period', 5)) * 60
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
                msg = u'{0} {1}'.format(prefix, alarm.name)
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

    @view_config(route_name='cloudwatch_alarms', renderer='json', request_method='PUT')
    def cloudwatch_alarms_update(self):
        message = json.loads(self.request.body)
        alarm = message.get('alarm', {})
        token = message.get('csrf_token')
        flash = message.get('flash')

        if not self.is_csrf_valid(token):
            return JSONResponse(status=400, message="missing CSRF token")

        name = alarm.get('name')
        metric = alarm.get('metric')
        namespace = alarm.get('namespace')
        statistic = alarm.get('statistic')
        comparison = alarm.get('comparison')
        threshold = alarm.get('threshold')
        period = alarm.get('period')
        evaluation_periods = alarm.get('evaluation_periods')
        unit = alarm.get('unit')
        description = alarm.get('description')
        dimensions = alarm.get('dimensions')

        metric_dimensions = {}
        for selected in dimensions:
            decoded = json.loads(selected)
            for key, value in decoded.iteritems():
                if key in metric_dimensions:
                    metric_dimensions[key] += value
                else:
                    metric_dimensions[key] = value

        updated = MetricAlarm(
            name=name, metric=metric, namespace=namespace, statistic=statistic,
            comparison=comparison, threshold=threshold, period=period,
            evaluation_periods=evaluation_periods, unit=unit, description=description,
            dimensions=metric_dimensions)

        with boto_error_handler(self.request):
            self.log_request(_(u'Updating alarm {0}').format(alarm.get('name')))
            action = self.cloudwatch_conn.put_metric_alarm(updated)

            if action:
                prefix = _(u'Successfully updated alarm')
            else:
                prefix = _(u'There was a problem deleting alarm')

            msg = u'{0} {1}'.format(prefix, alarm.get('name'))

        if flash is not None:
            self.request.session.flash(msg, queue=Notification.SUCCESS)

        return dict(success=action, message=msg)

    @view_config(route_name='cloudwatch_alarms', renderer='json', request_method='DELETE')
    def cloudwatch_alarms_delete(self):

        message = json.loads(self.request.body)
        alarms = message.get('alarms', [])
        token = message.get('csrf_token')
        flash = message.get('flash')

        if not self.is_csrf_valid(token):
            return JSONResponse(status=400, message="missing CSRF token")

        with boto_error_handler(self.request):
            self.log_request(_(u"Deleting alarm(s) {0}").format(alarms))
            action = self.cloudwatch_conn.delete_alarms(alarms)

            if action:
                prefix = _(u'Successfully deleted alarm(s)')
            else:
                prefix = _(u'There was a problem deleting alarm(s)')

            msg = u'{0} {1}'.format(prefix, ', '.join(alarms))

        if flash is not None:
            self.request.session.flash(msg, queue=Notification.SUCCESS)

        return dict(success=action, message=msg)

    def get_dimension_value(self, key=None):
        input_field = METRIC_DIMENSION_INPUTS.get(key)
        return [self.request.params.get(input_field)]

    @staticmethod
    def get_metric_unit_mapping():
        metric_units = {}
        for mtype in METRIC_TYPES:
            metric_units[mtype.get('name')] = mtype.get('unit')
        return metric_units

    @staticmethod
    def get_dimension_name(key=None):
        return METRIC_DIMENSION_NAMES.get(key)


class CloudWatchAlarmsJsonView(BaseView):
    """JSON response for CloudWatch Alarms landing page et. al."""
    @view_config(route_name='cloudwatch_alarms_json', renderer='json', request_method='POST')
    def cloudwatch_alarms_json(self):
        with boto_error_handler(self.request):
            items = self.get_items()
            alarms = []
            for alarm in items:
                alarms.append(dict(
                    name=alarm.name,
                    description=alarm.description,
                    ok_actions=alarm.ok_actions,
                    alarm_actions=alarm.alarm_actions,
                    insufficient_data_actions=alarm.insufficient_data_actions,
                    dimensions=alarm.dimensions,
                    statistic=alarm.statistic,
                    metric=alarm.metric,
                    period=alarm.period,
                    comparison=alarm.comparison,
                    threshold=alarm.threshold,
                    unit=alarm.unit,
                    state=alarm.state_value,
                ))
            return dict(results=alarms)

    @view_config(route_name="cloudwatch_alarms_for_metric_json", renderer='json', request_method='GET')
    def cloudwatch_alarm_for_metric_json(self):
        with boto_error_handler(self.request):
            metric_name = self.request.params.get('metric_name')
            namespace = self.request.params.get('namespace')
            statistic = self.request.params.get('statistic')
            period = self.request.params.get('period')
            items = self.get_alarms_for_metric(metric_name, namespace, statistic, period)
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

    @view_config(route_name="cloudwatch_alarms_for_resource_json", renderer='json', request_method='GET')
    def cloudwatch_alarms_for_resource_json(self):
        with boto_error_handler(self.request):
            res_id = self.request.matchdict.get('id')
            res_type = self.request.params.get('resource-type')

            items = Alarm.get_alarms_for_resource(
                res_id,
                cw_conn=self.get_connection(conn_type="cloudwatch"),
                dimension_key=res_type)
            alarms = []
            if items:
                for alarm in items:
                    alarms.append(dict(
                        name=alarm.name,
                        metric=alarm.metric,
                        comparison=alarm.comparison,
                        threshold=alarm.threshold,
                        unit=alarm.unit,
                        state=alarm.state_value
                    ))

            return dict(results=alarms)

    def get_items(self):
        conn = self.get_connection(conn_type='cloudwatch')
        return conn.describe_alarms() if conn else []

    def get_alarms_for_metric(self, metric_name, namespace, statistic, period):
        conn = self.get_connection(conn_type='cloudwatch')
        return conn.describe_alarms_for_metric(
            metric_name, namespace,
            period=period, statistic=statistic) if conn else []


class CloudWatchAlarmDetailView(BaseView):
    """CloudWatch Alarm detail page view."""

    TEMPLATE = '../templates/cloudwatch/alarms_detail.pt'

    def __init__(self, request, **kwargs):
        super(CloudWatchAlarmDetailView, self).__init__(request, **kwargs)

        alarm_id = self.request.matchdict.get('alarm_id')
        self.alarm = self.get_alarm(alarm_id)
        self.alarm_form = CloudWatchAlarmUpdateForm(
            request)

        self.render_dict = dict(
            alarm=self.alarm,
            alarm_id=alarm_id,
            alarm_form=self.alarm_form,
            search_facets=[]
        )

    @view_config(route_name='cloudwatch_alarm_view', renderer=TEMPLATE, request_method='GET')
    def cloudwatch_alarm_view(self):
        if not self.alarm:
            raise HTTPNotFound()

        dimensions = self.get_available_dimensions(self.alarm.metric)
        options = []
        for d in dimensions:
            for name, value in d.items():
                option = {
                    'label': '{0} = {1}'.format(name, ', '.join(value)),
                    'value': re.sub(r'\s+', '', json.dumps(d)),
                    'selected': value == self.alarm.dimensions.get(name)
                }
                options.append(option)

        alarm_json = json.dumps({
            'name': self.alarm.name,
            'state': self.alarm.state_value,
            'stateReason': self.alarm.state_reason,
            'metric': self.alarm.metric,
            'namespace': self.alarm.namespace,
            'statistic': self.alarm.statistic,
            'unit': self.alarm.unit,
            'dimensions': self.alarm.dimensions,
            'period': self.alarm.period,
            'evaluation_periods': self.alarm.evaluation_periods,
            'comparison': self.alarm.comparison,
            'threshold': self.alarm.threshold,
            'description': self.alarm.description
        })

        alarm_actions = []
        for action in self.alarm.alarm_actions:
            arn = AmazonResourceName.factory(action)
            policy_details = self.get_policies_for_scaling_group(arn.autoscaling_group_name, [arn.policy_name])
            policy_details.reverse()
            policy = policy_details.pop()

            detail = {
                'arn': arn.arn,
                'autoscaling_group_name': arn.autoscaling_group_name,
                'policy_name': arn.policy_name
            }

            if policy:
                detail['scaling_adjustment'] = policy.scaling_adjustment
            alarm_actions.append(detail)

        scaling_groups = self.get_scaling_groups()

        self.render_dict.update(
            alarm_json=alarm_json,
            metric_display_name=METRIC_TITLE_MAPPING.get(self.alarm.metric, self.alarm.metric),
            dimensions=dimensions,
            alarm_actions=alarm_actions,
            alarm_actions_json=json.dumps(alarm_actions),
            scaling_groups=scaling_groups,
            options=options
        )
        return self.render_dict

    def get_alarm(self, alarm_id):
        alarm = None
        conn = self.get_connection(conn_type='cloudwatch')
        with boto_error_handler(self.request):
            alarms = conn.describe_alarms(alarm_names=[alarm_id])
            if len(alarms) > 0:
                alarm = alarms[0]
        return alarm

    def get_available_dimensions(self, metric):
        dimensions = []
        conn = self.get_connection(conn_type='cloudwatch')
        with boto_error_handler(self.request):
            metrics = conn.list_metrics(metric_name=metric)
            for m in metrics:
                dimensions.append(m.dimensions)

        return dimensions

    def get_scaling_groups(self):
        conn = self.get_connection(conn_type='autoscale')
        with boto_error_handler(self.request):
            groups = conn.get_all_groups()
            return groups

    def get_policies_for_scaling_group(self, scaling_group, policy_names=None):
        conn = self.get_connection(conn_type='autoscale')
        with boto_error_handler(self.request):
            policies = conn.get_all_policies(as_group=scaling_group, policy_names=policy_names)
            return policies


class CloudWatchAlarmHistoryView(BaseView):
    """CloudWatch Alarm History page view."""

    TEMPLATE = '../templates/cloudwatch/alarms_history.pt'

    def __init__(self, request, **kwargs):
        super(CloudWatchAlarmHistoryView, self).__init__(request, **kwargs)

        self.alarm_id = self.request.matchdict.get('alarm_id')
        history = self.get_alarm_history(self.alarm_id)
        self.history = [{
            'timestamp': item.timestamp.isoformat(),
            'history_item_type': item.tem_type,
            'summary': item.summary} for item in history]

    @view_config(route_name='cloudwatch_alarm_history', renderer=TEMPLATE, request_method='GET')
    def cloudwatch_alarm_history_view(self):

        search_facets = [
            {'name': 'history_item_type', 'label': _(u"Type"), 'options': [
                {'key': 'ConfigurationUpdate', 'label': _("ConfigurationUpdate")},
                {'key': 'StateUpdate', 'label': _("StateUpdate")},
                {'key': 'Action', 'label': _("Action")}
            ]}
        ]

        return dict(
            alarm_id=self.alarm_id,
            history_json=json.dumps(self.history),
            filter_keys=[],
            search_facets=BaseView.escape_json(json.dumps(search_facets))
        )

    @view_config(route_name='cloudwatch_alarm_history_json', renderer='json', request_method='GET')
    def cloudwatch_alarm_history_json_view(self):
        return dict(
            history=self.history
        )

    def get_alarm_history(self, alarm_id):
        history = None
        conn = self.get_connection(conn_type='cloudwatch')
        with boto_error_handler(self.request):
            history = conn.describe_alarm_history(alarm_name=alarm_id)
        return history


class CloudWatchAlarmActionsView(BaseView):
    """CloudWatch Alarm Actions view."""

    def __init__(self, request, **kwargs):
        super(CloudWatchAlarmActionsView, self).__init__(request, **kwargs)

        self.alarm_id = self.request.matchdict.get('alarm_id')
        self.alarm = self.get_alarm(self.alarm_id)

    @view_config(route_name='cloudwatch_alarm_actions', renderer='json', request_method='PUT')
    def update_actions(self):
        if not self.alarm:
            raise HTTPNotFound()

        request = json.loads(self.request.body)
        request_actions = request.get('actions')
        actions = [action.get('arn') for action in request_actions]

        with boto_error_handler(self.request):
            # See https://github.com/boto/boto/issues/1311
            self.alarm.comparison = self.alarm._cmp_map.get(self.alarm.comparison)
            self.alarm.alarm_actions = actions
            self.alarm.update()

        return dict(
            success='success'
        )

    def get_alarm(self, alarm_id):
        alarm = None
        conn = self.get_connection(conn_type='cloudwatch')
        with boto_error_handler(self.request):
            alarms = conn.describe_alarms(alarm_names=[alarm_id])
            if len(alarms) > 0:
                alarm = alarms[0]
        return alarm
