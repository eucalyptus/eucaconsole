# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS instances

"""
from dateutil import parser
from pyramid.httpexceptions import HTTPNotFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.instances import InstanceForm
from ..models import LandingPageFilter
from ..views import LandingPageView, TaggedItemView


class InstancesView(LandingPageView):
    def __init__(self, request):
        super(InstancesView, self).__init__(request)
        self.items = self.get_items()
        self.initial_sort_key = '-launch_time'
        self.prefix = '/instances'

    def get_items(self):
        conn = self.get_connection()
        return conn.get_only_instances() if conn else []

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt')
    def instances_landing(self):
        json_items_endpoint = self.request.route_url('instances_json')
        status_choices = sorted(set(instance.state for instance in self.items))
        instance_type_choices = sorted(set(instance.instance_type for instance in self.items))
        avail_zone_choices = sorted(set(instance.placement for instance in self.items))
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        self.filter_fields = [
            LandingPageFilter(key='status', name=_(u'Status'), choices=status_choices),
            LandingPageFilter(key='instance_type', name=_(u'Instance type'), choices=instance_type_choices),
            LandingPageFilter(key='placement', name=_(u'Availability zone'), choices=avail_zone_choices),
        ]
        more_filter_keys = ['id', 'name', 'ip_address']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='-launch_time', name=_(u'Launch time (most recent first)')),
            dict(key='name', name=_(u'Instance name')),
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

    @view_config(route_name='instances_json', renderer='json', request_method='GET')
    def instances_json(self):
        instances = []
        for instance in self.items:
            instances.append(dict(
                id=instance.id,
                instance_type=instance.instance_type,
                ip_address=instance.ip_address,
                launch_time=instance.launch_time,
                placement=instance.placement,
                root_device=instance.root_device_name,
                security_groups=', '.join(group.name for group in instance.groups),
                status=instance.state,
            ))
        return dict(results=instances)


class InstanceView(TaggedItemView):
    VIEW_TEMPLATE = '../templates/instances/instance_view.pt'

    def __init__(self, request):
        super(InstanceView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.instance = self.get_instance()
        self.image = self.get_image()
        self.scaling_group = self.get_scaling_group()
        self.instance_form = InstanceForm(
            self.request, instance=self.instance, conn=self.conn, formdata=self.request.params or None)
        self.tagged_obj = self.instance
        self.launch_time = self.get_launch_time()
        self.render_dict = dict(
            instance=self.instance,
            image=self.image,
            scaling_group=self.scaling_group,
            instance_form=self.instance_form,
            instance_launch_time=self.launch_time,
        )

    @view_config(route_name='instance_view', renderer=VIEW_TEMPLATE)
    def instance_view(self):
        if self.instance is None:
            raise HTTPNotFound()
        return self.render_dict

    @view_config(route_name='instance_launch', renderer='../templates/instances/instance_launch.pt')
    def instance_launch(self):
        image_id = self.request.params.get('image_id')
        conn = self.get_connection()
        image = conn.get_image(image_id)
        return dict(
            image=image
        )

    def get_instance(self):
        instance_id = self.request.matchdict.get('id')
        if instance_id:
            instances_list = self.conn.get_only_instances(instance_ids=[instance_id])
            return instances_list[0] if instances_list else None
        return None

    def get_launch_time(self):
        """Returns instance launch time as a python datetime.datetime object"""
        if self.instance.launch_time:
            return parser.parse(self.instance.launch_time)
        return None

    def get_image(self):
        return self.conn.get_image(self.instance.image_id)

    def get_scaling_group(self):
        return self.instance.tags.get('aws:autoscaling:groupName')
