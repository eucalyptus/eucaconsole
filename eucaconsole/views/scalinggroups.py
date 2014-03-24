# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS scaling groups

"""
import simplejson as json
import time

from markupsafe import escape
from operator import attrgetter

from boto.ec2.autoscale import AutoScalingGroup, ScalingPolicy
from boto.ec2.autoscale.tag import Tag

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.alarms import CloudWatchAlarmCreateForm
from ..forms.scalinggroups import (
    ScalingGroupDeleteForm, ScalingGroupEditForm, ScalingGroupCreateForm, ScalingGroupInstancesMarkUnhealthyForm,
    ScalingGroupInstancesTerminateForm, ScalingGroupPolicyCreateForm, ScalingGroupPolicyDeleteForm)
from ..models import Notification
from ..views import LandingPageView, BaseView
from . import boto_error_handler


class DeleteScalingGroupMixin(object):
    def wait_for_instances_to_shutdown(self, scaling_group):
        if scaling_group.instances:
            ec2_conn = self.get_connection()
            instance_ids = [i.instance_id for i in scaling_group.instances]
            is_all_shutdown = False
            count = 0
            while is_all_shutdown is False and count < 30:
                instances = ec2_conn.get_only_instances(instance_ids)
                if instances:
                    is_all_shutdown = True
                    for instance in instances:
                        if self.cloud_type == 'aws':
                            if not str(instance._state).startswith('terminated'):
                                is_all_shutdown = False
                        else:
                            if not str(instance._state).startswith('terminated') and not str(instance._state).startswith('shutting-down'):
                                is_all_shutdown = False
                    time.sleep(3)
                count += 1
        return


class ScalingGroupsView(LandingPageView, DeleteScalingGroupMixin):
    TEMPLATE = '../templates/scalinggroups/scalinggroups.pt'

    def __init__(self, request):
        super(ScalingGroupsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/scalinggroups'
        self.delete_form = ScalingGroupDeleteForm(self.request, formdata=self.request.params or None)

    @view_config(route_name='scalinggroups', renderer=TEMPLATE, request_method='GET')
    def scalinggroups_landing(self):
        json_items_endpoint = self.request.route_path('scalinggroups_json')
        self.filter_keys = ['availability_zones', 'launch_config', 'name', 'placement_group']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='-status', name=_(u'Health status')),
            dict(key='-current_instances_count', name=_(u'Current instances')),
            dict(key='launch_config', name=_(u'Launch configuration')),
            dict(key='availability_zones', name=_(u'Availability zones')),
        ]
        return dict(
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
            delete_form=self.delete_form,
        )

    @view_config(route_name='scalinggroups_delete', request_method='POST', renderer=TEMPLATE)
    def scalinggroups_delete(self):
        if self.delete_form.validate():
            location = self.request.route_path('scalinggroups')
            name = self.request.params.get('name')
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Deleting scaling group {0}").format(name))
                conn = self.get_connection(conn_type='autoscale')
                scaling_group = self.get_scaling_group_by_name(name)
                # Need to shut down instances prior to scaling group deletion
                #TODO: in "this" case, we need to replace sleeps with polling loop to check state.
                scaling_group.shutdown_instances()
                self.wait_for_instances_to_shutdown(scaling_group)
                time.sleep(3)
                conn.delete_auto_scaling_group(name)
                prefix = _(u'Successfully deleted scaling group')
                msg = '{0} {1}'.format(prefix, name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    def get_scaling_group_by_name(self, name):
        conn = self.get_connection(conn_type='autoscale')
        names = []
        names.append(name)
        return conn.get_all_groups(names)[0] if conn else []


class ScalingGroupsJsonView(BaseView):
    @view_config(route_name='scalinggroups_json', renderer='json', request_method='GET')
    def scalinggroups_json(self):
        scalinggroups = []
        with boto_error_handler(self.request):
            items = self.get_items()
        for group in items:
            group_instances = group.instances or []
            all_healthy = all(instance.health_status == 'Healthy' for instance in group_instances)
            scalinggroups.append(dict(
                availability_zones=', '.join(sorted(group.availability_zones)),
                load_balancers=', '.join(sorted(group.load_balancers)),
                desired_capacity=group.desired_capacity,
                launch_config=group.launch_config_name,
                max_size=group.max_size,
                min_size=group.min_size,
                name=group.name,
                placement_group=group.placement_group,
                termination_policies=', '.join(group.termination_policies),
                current_instances_count=len(group_instances),
                status='Healthy' if all_healthy else 'Unhealthy',
            ))
        return dict(results=scalinggroups)

    def get_items(self):
        conn = self.get_connection(conn_type='autoscale')
        return conn.get_all_groups() if conn else []


class BaseScalingGroupView(BaseView):
    def __init__(self, request):
        super(BaseScalingGroupView, self).__init__(request)
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.cloudwatch_conn = self.get_connection(conn_type='cloudwatch')
        self.elb_conn = self.get_connection(conn_type='elb')
        self.ec2_conn = self.get_connection()

    def get_scaling_group(self):
        scalinggroup_param = self.request.matchdict.get('id')  # id = scaling_group.name
        scalinggroups_param = [scalinggroup_param]
        scaling_groups = []
        if self.autoscale_conn:
            scaling_groups = self.autoscale_conn.get_all_groups(names=scalinggroups_param)
        return scaling_groups[0] if scaling_groups else None

    def get_alarms(self):
        if self.cloudwatch_conn:
            return self.cloudwatch_conn.describe_alarms()
        return []

    def get_policies(self, scaling_group):
        policies = []
        if self.autoscale_conn:
            policies = self.autoscale_conn.get_all_policies(as_group=scaling_group.name)
        return sorted(policies)

    def parse_tags_param(self, scaling_group_name=None):
        tags_json = self.request.params.get('tags')
        tags_list = json.loads(tags_json) if tags_json else []
        tags = []
        for tag in tags_list:
            tags.append(Tag(
                resource_id=scaling_group_name,
                key=escape(tag.get('name')),
                value=escape(tag.get('value')),
                propagate_at_launch=tag.get('propagate_at_launch', False),
            ))
        return tags


class ScalingGroupView(BaseScalingGroupView, DeleteScalingGroupMixin):
    """Views for Scaling Group detail page"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_view.pt'

    def __init__(self, request):
        super(ScalingGroupView, self).__init__(request)
        with boto_error_handler(request):
            self.scaling_group = self.get_scaling_group()
            self.policies = self.get_policies(self.scaling_group)
        self.edit_form = ScalingGroupEditForm(
            self.request, scaling_group=self.scaling_group, autoscale_conn=self.autoscale_conn, ec2_conn=self.ec2_conn,
            elb_conn=self.elb_conn, formdata=self.request.params or None)
        self.delete_form = ScalingGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            policies=self.policies,
            edit_form=self.edit_form,
            delete_form=self.delete_form,
            avail_zone_placeholder_text=_(u'Select one or more availability zones...'),
            termination_policies_placeholder_text=_(u'Select one or more termination policies...')
        )

    @view_config(route_name='scalinggroup_view', renderer=TEMPLATE)
    def scalinggroup_view(self):
        return self.render_dict

    @view_config(route_name='scalinggroup_update', request_method='POST', renderer=TEMPLATE)
    def scalinggroup_update(self):
        if self.edit_form.validate():
            location = self.request.route_path('scalinggroup_view', id=self.scaling_group.name)
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Updating scaling group {0}").format(self.scaling_group.name))
                self.update_tags()
                self.update_properties()
                prefix = _(u'Successfully updated scaling group')
                msg = '{0} {1}'.format(prefix, self.scaling_group.name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='scalinggroup_delete', request_method='POST', renderer=TEMPLATE)
    def scalinggroup_delete(self):
        if self.delete_form.validate():
            location = self.request.route_path('scalinggroups')
            name = self.request.params.get('name')
            with boto_error_handler(self.request, location):
                # Need to shut down instances prior to scaling group deletion
                #TODO: in "this" case, we need to replace sleeps with polling loop to check state.
                self.log_request(_(u"Terminating scaling group {0} instances").format(name))
                self.scaling_group.shutdown_instances()
                self.wait_for_instances_to_shutdown(self.scaling_group)
                time.sleep(3)
                self.log_request(_(u"Deleting scaling group {0}").format(name))
                self.autoscale_conn.delete_auto_scaling_group(name)
                prefix = _(u'Successfully deleted scaling group')
                msg = '{0} {1}'.format(prefix, name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    def update_tags(self):
        updated_tags_list = self.parse_tags_param(scaling_group_name=self.scaling_group.name)
        # Delete existing tags first
        if self.scaling_group.tags:
            self.autoscale_conn.delete_tags(self.scaling_group.tags)
        self.autoscale_conn.create_or_update_tags(updated_tags_list)

    def update_properties(self):
        self.scaling_group.desired_capacity = self.request.params.get('desired_capacity', 1)
        self.scaling_group.launch_config_name = self.request.params.get('launch_config')
        self.scaling_group.availability_zones = self.request.params.getall('availability_zones')  # getall = multiselect
        self.scaling_group.termination_policies = self.request.params.getall('termination_policies')
        self.scaling_group.max_size = self.request.params.get('max_size', 1)
        self.scaling_group.min_size = self.request.params.get('min_size', 0)
        self.scaling_group.health_check_type = self.request.params.get('health_check_type')
        self.scaling_group.health_check_period = self.request.params.get('health_check_period', 120)
        self.scaling_group.default_cooldown = self.request.params.get('default_cooldown', 120)
        self.scaling_group.update()


class ScalingGroupInstancesView(BaseScalingGroupView):
    """View for Scaling Group Manage Instances page"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_instances.pt'

    def __init__(self, request):
        super(ScalingGroupInstancesView, self).__init__(request)
        self.scaling_group = self.get_scaling_group()
        self.policies = self.get_policies(self.scaling_group)
        self.markunhealthy_form = ScalingGroupInstancesMarkUnhealthyForm(
            self.request, formdata=self.request.params or None)
        self.terminate_form = ScalingGroupInstancesTerminateForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            policies=self.policies,
            markunhealthy_form=self.markunhealthy_form,
            terminate_form=self.terminate_form,
            json_items_endpoint=self.request.route_path('scalinggroup_instances_json', id=self.scaling_group.name),
        )

    @view_config(route_name='scalinggroup_instances', renderer=TEMPLATE, request_method='GET')
    def scalinggroup_instances(self):
        return self.render_dict

    @view_config(route_name='scalinggroup_instances_markunhealthy', renderer=TEMPLATE, request_method='POST')
    def scalinggroup_instances_markunhealthy(self):
        location = self.request.route_path('scalinggroup_instances', id=self.scaling_group.name)
        if self.markunhealthy_form.validate():
            instance_id = self.request.params.get('instance_id')
            respect_grace_period = self.request.params.get('respect_grace_period') == 'y'
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Marking instance {0} unhealthy").format(instance_id))
                self.autoscale_conn.set_instance_health(
                    instance_id, 'Unhealthy', should_respect_grace_period=respect_grace_period)
                prefix = _(u'Successfully marked the following instance as unhealthy:')
                msg = '{0} {1}'.format(prefix, instance_id)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.markunhealthy_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='scalinggroup_instances_terminate', renderer=TEMPLATE, request_method='POST')
    def scalinggroup_instances_terminate(self):
        location = self.request.route_path('scalinggroup_instances', id=self.scaling_group.name)
        if self.terminate_form.validate():
            instance_id = self.request.params.get('instance_id')
            decrement_capacity = self.request.params.get('decrement_capacity') == 'y'
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Terminating scaling group {0} instance {1}").format(self.scaling_group.name, instance_id))
                self.autoscale_conn.terminate_instance(instance_id, decrement_capacity=decrement_capacity)
                prefix = _(u'Successfully sent terminate request for instance')
                msg = '{0} {1}'.format(prefix, instance_id)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.terminate_form.get_errors_list()
        return self.render_dict


class ScalingGroupInstancesJsonView(BaseScalingGroupView):
    """JSON response for Scaling Group Manage Instances page"""

    def __init__(self, request):
        super(ScalingGroupInstancesJsonView, self).__init__(request)
        self.scaling_group = self.get_scaling_group()

    @view_config(route_name='scalinggroup_instances_json', renderer='json', request_method='GET')
    def scalinggroup_instances_json(self):
        instances = []
        transitional_states = ['Unhealthy', 'Pending']
        with boto_error_handler(self.request):
            items = self.get_instances()
        for instance in items:
            is_transitional = any([
                instance.lifecycle_state in transitional_states,
                instance.health_status in transitional_states,
            ])
            instances.append(dict(
                id=instance.instance_id,
                status=instance.health_status,
                availability_zone=instance.availability_zone,
                launch_config=instance.launch_config_name,
                lifecycle_state=instance.lifecycle_state,
                transitional=is_transitional,
            ))
        return dict(results=instances)

    def get_instances(self):
        if self.scaling_group.instances is None:
            return []
        return sorted(self.scaling_group.instances, key=attrgetter('instance_id'))


class ScalingGroupPoliciesView(BaseScalingGroupView):
    """View for Scaling Group Policies page"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_policies.pt'

    def __init__(self, request):
        super(ScalingGroupPoliciesView, self).__init__(request)
        with boto_error_handler(request):
            self.scaling_group = self.get_scaling_group()
            self.policies = self.get_policies(self.scaling_group)
            self.alarms = self.get_alarms()
            self.metrics = self.cloudwatch_conn.list_metrics()
        self.create_form = ScalingGroupPolicyCreateForm(
            self.request, scaling_group=self.scaling_group, alarms=self.alarms, formdata=self.request.params or None)
        self.delete_form = ScalingGroupPolicyDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            create_form=self.create_form,
            delete_form=self.delete_form,
            policies=self.policies,
            scale_down_text=_(u'Scale down by'),
            scale_up_text=_(u'Scale up by'),
        )

    @view_config(route_name='scalinggroup_policies', renderer=TEMPLATE, request_method='GET')
    def scalinggroup_policies(self):
        return self.render_dict

    @view_config(route_name='scalinggroup_policy_delete', renderer=TEMPLATE, request_method='POST')
    def scalinggroup_policy_delete(self):
        if self.delete_form.validate():
            location = self.request.route_path('scalinggroup_policies', id=self.scaling_group.name)
            policy_name = self.request.params.get('name')
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Deleting scaling group {0} policy {1}").format(self.scaling_group.name, policy_name))
                self.autoscale_conn.delete_policy(policy_name, autoscale_group=self.scaling_group.name)
                prefix = _(u'Successfully deleted scaling group policy')
                msg = '{0} {1}'.format(prefix, policy_name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict


class ScalingGroupPolicyView(BaseScalingGroupView):
    """View for creating a Scaling Group policy"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_policy.pt'

    def __init__(self, request):
        super(ScalingGroupPolicyView, self).__init__(request)
        with boto_error_handler(request):
            self.scaling_group = self.get_scaling_group()
            self.alarms = self.get_alarms()
            self.metrics = self.get_metrics()
        self.policy_form = ScalingGroupPolicyCreateForm(
            self.request, scaling_group=self.scaling_group, alarms=self.alarms, formdata=self.request.params or None)
        self.alarm_form = CloudWatchAlarmCreateForm(
            self.request, ec2_conn=self.ec2_conn, autoscale_conn=self.autoscale_conn, elb_conn=self.elb_conn,
            metrics=self.metrics, scaling_group=self.scaling_group, formdata=self.request.params or None)
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            policy_form=self.policy_form,
            alarm_form=self.alarm_form,
            create_alarm_redirect=self.request.route_path('scalinggroup_policy_new', id=self.scaling_group.name),
            scale_down_text=_(u'Scale down by'),
            scale_up_text=_(u'Scale up by'),
        )

    @view_config(route_name='scalinggroup_policy_new', renderer=TEMPLATE, request_method='GET')
    def scalinggroup_policy_new(self):
        return self.render_dict

    @view_config(route_name='scalinggroup_policy_create', renderer=TEMPLATE, request_method='POST')
    def scalinggroup_policy_create(self):
        location = self.request.route_path('scalinggroup_policies', id=self.scaling_group.name)
        if self.policy_form.validate():
            adjustment_amount = self.request.params.get('adjustment_amount')
            adjustment_direction = self.request.params.get('adjustment_direction', 'up')
            scaling_adjustment = adjustment_amount
            if adjustment_direction == 'down':
                scaling_adjustment = -adjustment_direction
            scaling_policy = ScalingPolicy(
                name=self.request.params.get('name'),
                as_name=self.scaling_group.name,
                adjustment_type=self.request.params.get('adjustment_type'),
                scaling_adjustment=scaling_adjustment,
                cooldown=self.request.params.get('cooldown'),
            )
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Creating scaling group {0} policy {1}").format(self.scaling_group.name, scaling_policy.name))
                # Create scaling policy
                self.autoscale_conn.create_scaling_policy(scaling_policy)
                created_scaling_policy = self.autoscale_conn.get_all_policies(
                    as_group=self.scaling_group.name, policy_names=[scaling_policy.name])[0]
                # Attach policy to alarm
                alarm_name = self.request.params.get('alarm')
                alarm = self.cloudwatch_conn.describe_alarms(alarm_names=[alarm_name])[0]
                alarm.dimensions.update({"AutoScalingGroupName": self.scaling_group.name})
                alarm.comparison = alarm._cmp_map.get(alarm.comparison)  # See https://github.com/boto/boto/issues/1311
                # TODO: Detect if an alarm has 5 scaling policies attached to it and abort accordingly
                if created_scaling_policy.policy_arn not in alarm.alarm_actions:
                    alarm.alarm_actions.append(created_scaling_policy.policy_arn)
                alarm.update()
                prefix = _(u'Successfully created scaling group policy')
                msg = '{0} {1}'.format(prefix, scaling_policy.name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.policy_form.get_errors_list()
        return self.render_dict

    def get_metrics(self):
        return self.cloudwatch_conn.list_metrics()


class ScalingGroupWizardView(BaseScalingGroupView):
    """View for Create Scaling Group wizard"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_wizard.pt'

    def __init__(self, request):
        super(ScalingGroupWizardView, self).__init__(request)
        self.request = request
        with boto_error_handler(request):
            self.create_form = ScalingGroupCreateForm(
                self.request, autoscale_conn=self.autoscale_conn, ec2_conn=self.ec2_conn,
                elb_conn=self.elb_conn, formdata=self.request.params or None)
        self.render_dict = dict(
            create_form=self.create_form,
            avail_zones_placeholder_text=_(u'Select availability zones...')
        )

    @view_config(route_name='scalinggroup_new', renderer=TEMPLATE, request_method='GET')
    def scalinggroup_new(self):
        """Displays the Launch Instance wizard"""
        return self.render_dict

    @view_config(route_name='scalinggroup_create', renderer=TEMPLATE, request_method='POST')
    def scalinggroup_create(self):
        """Handles the POST from the Create Scaling Group wizard"""
        if self.create_form.validate():
            with boto_error_handler(self.request, self.request.route_path('scalinggroups')):
                scaling_group_name = self.request.params.get('name')
                self.log_request(_(u"Creating scaling group {0}").format(scaling_group_name))
                scaling_group = AutoScalingGroup(
                    name=scaling_group_name,
                    launch_config=self.request.params.get('launch_config'),
                    availability_zones=self.request.params.getall('availability_zones'),
                    load_balancers=self.request.params.getall('load_balancers'),
                    health_check_type=self.request.params.get('health_check_type'),
                    health_check_period=self.request.params.get('health_check_period'),
                    desired_capacity=self.request.params.get('desired_capacity'),
                    min_size=self.request.params.get('min_size'),
                    max_size=self.request.params.get('max_size'),
                    tags=self.parse_tags_param(scaling_group_name=scaling_group_name),
                )
                self.autoscale_conn.create_auto_scaling_group(scaling_group)
                msg = _(u'Successfully created scaling group')
                msg += ' {0}'.format(scaling_group.name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                location = self.request.route_path('scalinggroup_view', id=scaling_group.name)
                return HTTPFound(location=location)
        return self.render_dict


