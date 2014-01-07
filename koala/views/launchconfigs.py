# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS launch configurations

"""
import re

from boto.ec2.autoscale.launchconfig import LaunchConfiguration
from boto.exception import EC2ResponseError

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config
import time

from ..forms.launchconfigs import LaunchConfigDeleteForm, CreateLaunchConfigForm
from ..models import Notification
from ..views import LandingPageView, BaseView, BlockDeviceMappingItemView


class LaunchConfigsView(LandingPageView):
    def __init__(self, request):
        super(LaunchConfigsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/launchconfigs'

    @view_config(route_name='launchconfigs', renderer='../templates/launchconfigs/launchconfigs.pt')
    def launchconfigs_landing(self):
        json_items_endpoint = self.request.route_url('launchconfigs_json')
        self.filter_keys = ['image_id', 'key_name', 'kernel_id', 'name', 'ramdisk_id', 'security_groups']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name='Name'),
            dict(key='-created_time', name='Created time (recent first)'),
            dict(key='image_id', name='Image ID'),
            dict(key='key_name', name='Key pair'),
            dict(key='instance_monitoring', name='Instance monitoring'),
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


class LaunchConfigsJsonView(BaseView):
    """JSON response view for Launch Configurations landing page"""
    @view_config(route_name='launchconfigs_json', renderer='json', request_method='GET')
    def launchconfigs_json(self):
        launchconfigs = []
        for launchconfig in self.get_items():
            security_groups = ', '.join(launchconfig.security_groups)
            launchconfigs.append(dict(
                created_time=launchconfig.created_time.isoformat(),
                image_id=launchconfig.image_id,
                instance_monitoring='monitored' if bool(launchconfig.instance_monitoring) else 'unmonitored',
                kernel_id=launchconfig.kernel_id,
                key_name=launchconfig.key_name,
                name=launchconfig.name,
                ramdisk_id=launchconfig.ramdisk_id,
                security_groups=security_groups,
            ))
        return dict(results=launchconfigs)

    def get_items(self):
        conn = self.get_connection(conn_type='autoscale')
        return conn.get_all_launch_configurations() if conn else []


class LaunchConfigView(BaseView):
    """Views for single LaunchConfig"""
    TEMPLATE = '../templates/launchconfigs/launchconfig_view.pt'

    def __init__(self, request):
        super(LaunchConfigView, self).__init__(request)
        self.conn = self.get_connection(conn_type='autoscale')
        self.launchconfig = self.get_launchconfig()
        self.delete_form = LaunchConfigDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            launchconfig=self.launchconfig,
            delete_form=self.delete_form,
        )

    def get_launchconfig(self):
        launchconfig_param = self.request.matchdict.get('id')
        launchconfigs_param = [launchconfig_param]
        launchconfigs = self.conn.get_all_launch_configurations(names=launchconfigs_param)
        launchconfigs = launchconfigs[0] if launchconfigs else None
        return launchconfigs 

    @view_config(route_name='launchconfig_view', renderer=TEMPLATE)
    def launchconfig_view(self):
        self.launchconfig.instance_monitoring_boolean = re.match(
            r'InstanceMonitoring\((\w+)\)', str(self.launchconfig.instance_monitoring)).group(1)
        self.launchconfig.security_groups_str = ', '.join(self.launchconfig.security_groups)
        return self.render_dict
 
    @view_config(route_name='launchconfig_delete', request_method='POST', renderer=TEMPLATE)
    def launchconfig_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            try:
                self.conn.delete_launch_configuration(name)
                prefix = _(u'Successfully deleted launchconfig')
                msg = '{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            location = self.request.route_url('launchconfigs')
            return HTTPFound(location=location)

        return self.render_dict


class CreateLaunchConfigView(BlockDeviceMappingItemView):
    TEMPLATE = '../templates/launchconfigs/launchconfig_wizard.pt'

    def __init__(self, request):
        super(CreateLaunchConfigView, self).__init__(request)
        self.request = request
        self.image = self.get_image()
        self.create_form = CreateLaunchConfigForm(
            self.request, image=self.image, conn=self.conn, formdata=self.request.params or None)
        self.images_json_endpoint = self.request.route_url('images_json')
        self.owner_choices = self.get_owner_choices()
        self.render_dict = dict(
            image=self.image,
            create_form=self.create_form,
            images_json_endpoint=self.images_json_endpoint,
            owner_choices=self.owner_choices,
            snapshot_choices=self.get_snapshot_choices(),
        )

    @view_config(route_name='launchconfig_new', renderer=TEMPLATE, request_method='GET')
    def launchconfig_new(self):
        """Displays the Create Launch Configuration wizard"""
        return self.render_dict

    @view_config(route_name='launchconfig_create', renderer=TEMPLATE, request_method='POST')
    def launchconfig_create(self):
        """Handles the POST from the Create Launch Configuration wizard"""
        if self.create_form.validate():
            autoscale_conn = self.get_connection(conn_type='autoscale')
            location = self.request.route_url('launchconfigs')
            image_id = self.image.id
            name=self.request.params.get('name')
            key_name = self.request.params.get('keypair')
            securitygroup = self.request.params.get('securitygroup', 'default')
            security_groups = [securitygroup]  # Security group names
            instance_type = self.request.params.get('instance_type', 'm1.small')
            user_data = self.request.params.get('user_data')
            kernel_id = self.request.params.get('kernel_id') or None
            ramdisk_id = self.request.params.get('ramdisk_id') or None
            monitoring_enabled = self.request.params.get('monitoring_enabled', False)
            bdmapping_json = self.request.params.get('block_device_mapping')
            block_device_mappings = [self.get_block_device_map(bdmapping_json)]
            try:
                launch_config = LaunchConfiguration(
                    name=name, image_id=image_id, key_name=key_name, security_groups=security_groups,
                    user_data=user_data, instance_type=instance_type, kernel_id=kernel_id, ramdisk_id=ramdisk_id,
                    block_device_mappings=block_device_mappings, instance_monitoring=monitoring_enabled
                )
                autoscale_conn.create_launch_configuration(launch_config=launch_config)
                time.sleep(2)
                msg = _(u'Successfully sent create launch configuration request. '
                        u'It may take a moment to create the launch configuration.')
                queue = Notification.SUCCESS
                self.request.session.flash(msg, queue=queue)
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
                self.request.session.flash(msg, queue=queue)
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict


