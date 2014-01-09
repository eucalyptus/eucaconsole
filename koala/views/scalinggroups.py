# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS scaling groups

"""
from operator import attrgetter

import simplejson as json

from boto.ec2.autoscale.tag import Tag
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.scalinggroups import ScalingGroupDeleteForm, ScalingGroupEditForm, ScalingGroupPolicyDeleteForm
from ..models import Notification
from ..views import LandingPageView, BaseView


class ScalingGroupsView(LandingPageView):
    def __init__(self, request):
        super(ScalingGroupsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/scalinggroups'
        self.display_type = self.request.params.get('display', 'tableview')  # Set tableview as default

    @view_config(route_name='scalinggroups', renderer='../templates/scalinggroups/scalinggroups.pt')
    def scalinggroups_landing(self):
        json_items_endpoint = self.request.route_url('scalinggroups_json')
        self.filter_keys = ['availability_zones', 'launch_config', 'name', 'placement_group']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name')),
            dict(key='launch_config', name=_(u'Launch configuration')),
            dict(key='availability_zones', name=_(u'Availability zones')),
        ]
        return dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
        )


class ScalingGroupsJsonView(BaseView):
    @view_config(route_name='scalinggroups_json', renderer='json', request_method='GET')
    def scalinggroups_json(self):
        scalinggroups = []
        for group in self.get_items():
            scalinggroups.append(dict(
                availability_zones=', '.join(group.availability_zones),
                desired_capacity=group.desired_capacity,
                launch_config=group.launch_config_name,
                max_size=group.max_size,
                min_size=group.min_size,
                name=group.name,
                placement_group=group.placement_group,
                termination_policies=', '.join(group.termination_policies),
                instance_ids=[instance.instance_id for instance in group.instances],
            ))
        return dict(results=scalinggroups)

    def get_items(self):
        conn = self.get_connection(conn_type='autoscale')
        return conn.get_all_groups() if conn else []


class BaseScalingGroupView(BaseView):
    def __init__(self, request):
        super(BaseScalingGroupView, self).__init__(request)
        self.conn = self.get_connection(conn_type='autoscale')
        self.ec2_conn = self.get_connection()

    def get_scaling_group(self):
        scalinggroup_param = self.request.matchdict.get('id')  # id = scaling_group.name
        scalinggroups_param = [scalinggroup_param]
        scaling_groups = self.conn.get_all_groups(names=scalinggroups_param)
        return scaling_groups[0] if scaling_groups else None


class ScalingGroupView(BaseScalingGroupView):
    """Views for Scaling Group detail page"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_view.pt'

    def __init__(self, request):
        super(ScalingGroupView, self).__init__(request)
        self.scaling_group = self.get_scaling_group()
        self.edit_form = ScalingGroupEditForm(
            self.request, scaling_group=self.scaling_group, autoscale_conn=self.conn, ec2_conn=self.ec2_conn,
            formdata=self.request.params or None)
        self.delete_form = ScalingGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            scaling_group=self.scaling_group,
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
            location = self.request.route_url('scalinggroup_view', id=self.scaling_group.name)
            try:
                self.update_tags()
                self.update_properties()
                prefix = _(u'Successfully updated scaling group')
                msg = '{0} {1}'.format(prefix, self.scaling_group.name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='scalinggroup_delete', request_method='POST', renderer=TEMPLATE)
    def scalinggroup_delete(self):
        if self.delete_form.validate():
            location = self.request.route_url('scalinggroups')
            name = self.request.params.get('name')
            try:
                self.conn.delete_auto_scaling_group(name, force_delete=True)
                prefix = _(u'Successfully deleted scaling group')
                msg = '{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    def parse_tags_param(self):
        tags_json = self.request.params.get('tags')
        tags_list = json.loads(tags_json) if tags_json else []
        tags = []
        for tag in tags_list:
            tags.append(Tag(
                resource_id=self.scaling_group.name,
                key=tag.get('name'),
                value=tag.get('value'),
                propagate_at_launch=tag.get('propagate_at_launch', False),
            ))
        return tags

    def update_tags(self):
        updated_tags_list = self.parse_tags_param()
        # Delete existing tags first
        if self.scaling_group.tags:
            self.conn.delete_tags(self.scaling_group.tags)
        self.conn.create_or_update_tags(updated_tags_list)

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
        self.instances = self.get_instances()
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            instances=self.instances,
        )

    @view_config(route_name='scalinggroup_instances', renderer=TEMPLATE)
    def scalinggroup_instances(self):
        return self.render_dict

    def get_instances(self):
        return sorted(self.scaling_group.instances, key=attrgetter('instance_id'))


class ScalingGroupAlarmsView(BaseScalingGroupView):
    """View for Scaling Group Alarms page"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_alarms.pt'

    def __init__(self, request):
        super(ScalingGroupAlarmsView, self).__init__(request)
        self.scaling_group = self.get_scaling_group()
        self.alarms = self.get_alarms()
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            alarms=self.alarms,
        )

    @view_config(route_name='scalinggroup_alarms', renderer=TEMPLATE)
    def scalinggroup_alarms(self):
        return self.render_dict

    def get_alarms(self):
        # TODO: Implement
        return []


class ScalingGroupPoliciesView(BaseScalingGroupView):
    """View for Scaling Group Policies page"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_policies.pt'

    def __init__(self, request):
        super(ScalingGroupPoliciesView, self).__init__(request)
        self.scaling_group = self.get_scaling_group()
        self.policies = self.get_policies()
        self.delete_form = ScalingGroupPolicyDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            delete_form=self.delete_form,
            policies=self.policies,
            scale_down_text=_(u'Scale down by'),
            scale_up_text=_(u'Scale up by'),
        )

    @view_config(route_name='scalinggroup_policies', renderer=TEMPLATE)
    def scalinggroup_policies(self):
        return self.render_dict

    @view_config(route_name='scalinggroup_policy_delete', renderer=TEMPLATE)
    def scalinggroup_policy_delete(self):
        if self.delete_form.validate():
            location = self.request.route_url('scalinggroup_policies')
            policy_name = self.request.params.get('name')
            try:
                self.conn.delete_policiy(policy_name, autoscale_group=self.scaling_group.name)
                prefix = _(u'Successfully deleted scaling group policy')
                msg = '{0} {1}'.format(prefix, policy_name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    def get_policies(self):
        policies = self.conn.get_all_policies(as_group=self.scaling_group.name)
        return sorted(policies)

