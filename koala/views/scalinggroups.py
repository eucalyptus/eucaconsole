# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS scaling groups

"""
import simplejson as json

from boto.ec2.autoscale.tag import Tag
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.scalinggroups import ScalingGroupDeleteForm, ScalingGroupEditForm
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
            ))
        return dict(results=scalinggroups)

    def get_items(self):
        conn = self.get_connection(conn_type='autoscale')
        return conn.get_all_groups() if conn else []


class ScalingGroupView(BaseView):
    """Views for single ScalingGroup"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_view.pt'

    def __init__(self, request):
        super(ScalingGroupView, self).__init__(request)
        self.conn = self.get_connection(conn_type='autoscale')
        self.ec2_conn = self.get_connection()
        self.scaling_group = self.get_scaling_group()
        self.edit_form = ScalingGroupEditForm(
            self.request, scaling_group=self.scaling_group, autoscale_conn=self.conn, ec2_conn=self.ec2_conn,
            formdata=self.request.params or None)
        self.delete_form = ScalingGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            edit_form=self.edit_form,
            delete_form=self.delete_form,
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

    def get_scaling_group(self):
        scalinggroup_param = self.request.matchdict.get('id')  # id = scaling_group.name
        scalinggroups_param = [scalinggroup_param]
        scaling_groups = self.conn.get_all_groups(names=scalinggroups_param)
        return scaling_groups[0] if scaling_groups else None

    def parse_tags_param(self):
        tags_json = self.request.params.get('tags')
        tags_list = json.loads(tags_json) if tags_json else []
        tags = []
        for tag in tags_list:
            tags.append(Tag(
                resource_id=self.scaling_group.name,
                key=tag.get('name'),
                value=tag.get('value'),
                propagate_at_launch=tag.get('propatage_at_launch', False),
            ))
        return tags

    def update_tags(self):
        updated_tags_list = self.parse_tags_param()
        # Delete existing tags first
        if self.scaling_group.tags:
            self.conn.delete_tags(self.scaling_group.tags)
        self.conn.create_or_update_tags(updated_tags_list)

    def update_properties(self):
        desired_capacity = self.request.params.get('desired_capacity', 1)
        self.scaling_group.set_capacity(desired_capacity)
        self.scaling_group.launch_config_name = self.request.params.get('launch_config')
        self.scaling_group.availability_zones = self.request.params.getall('availability_zones')  # getall = multiselect
        self.scaling_group.max_size = self.request.params.get('max_size', 1)
        self.scaling_group.min_size = self.request.params.get('min_size', 0)
        self.scaling_group.health_check_type = self.request.params.get('health_check_type')
        self.scaling_group.health_check_period = self.request.params.get('health_check_period', 120)
        self.scaling_group.update()


