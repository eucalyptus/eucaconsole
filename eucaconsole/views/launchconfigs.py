# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS launch configurations

"""
from urllib import quote
import simplejson as json

from boto.ec2.autoscale.launchconfig import LaunchConfiguration

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms import GenerateFileForm
from ..forms.images import ImagesFiltersForm
from ..forms.keypairs import KeyPairForm
from ..forms.launchconfigs import LaunchConfigDeleteForm, CreateLaunchConfigForm, LaunchConfigsFiltersForm
from ..forms.securitygroups import SecurityGroupForm
from ..models import Notification
from ..views import LandingPageView, BaseView, BlockDeviceMappingItemView
from ..views.images import ImageView
from ..views.securitygroups import SecurityGroupsView
from . import boto_error_handler


class LaunchConfigsView(LandingPageView):
    def __init__(self, request):
        super(LaunchConfigsView, self).__init__(request)
        self.request = request
        self.ec2_conn = self.get_connection()
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.initial_sort_key = 'name'
        self.prefix = '/launchconfigs'
        self.filter_keys = ['image_id', 'image_name', 'key_name', 'name', 'security_groups']
        self.sort_keys = self.get_sort_keys()
        self.json_items_endpoint = self.get_json_endpoint('launchconfigs_json')
        self.delete_form = LaunchConfigDeleteForm(self.request, formdata=self.request.params or None)
        self.filters_form = LaunchConfigsFiltersForm(
            self.request, cloud_type=self.cloud_type, ec2_conn=self.ec2_conn, formdata=self.request.params or None)
        self.render_dict = dict(
            filter_fields=True,
            filters_form=self.filters_form,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
            delete_form=self.delete_form,
        )

    @view_config(route_name='launchconfigs', renderer='../templates/launchconfigs/launchconfigs.pt')
    def launchconfigs_landing(self):
        # sort_keys are passed to sorting drop-down
        return self.render_dict

    @view_config(route_name='launchconfigs_delete', request_method='POST')
    def launchconfigs_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            location = self.request.route_path('launchconfigs')
            prefix = _(u'Unable to delete launch configuration')
            template = '{0} {1} - {2}'.format(prefix, name, '{0}')
            with boto_error_handler(self.request, location, template):
                self.autoscale_conn.delete_launch_configuration(name)
                prefix = _(u'Successfully deleted launch configuration.')
                msg = '{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
                notification_msg = msg
                self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    @staticmethod
    def get_sort_keys():
        return [
            dict(key='name', name='Name: A to Z'),
            dict(key='-name', name='Name: Z to A'),
            dict(key='created_time', name='Creation time: Oldest to Newest'),
            dict(key='-created_time', name='Creation time: Newest to Oldest'),
            dict(key='image_name', name='Image Name: A to Z'),
            dict(key='-image_name', name='Image Name: Z to A'),
            dict(key='key_name', name='Key pair: A to Z'),
            dict(key='-key_name', name='Key pair: Z to A'),
        ]


class LaunchConfigsJsonView(LandingPageView):
    """JSON response view for Launch Configurations landing page"""
    def __init__(self, request):
        super(LaunchConfigsJsonView, self).__init__(request)
        self.ec2_conn = self.get_connection()
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        with boto_error_handler(request):
            self.items = self.get_items()

    @view_config(route_name='launchconfigs_json', renderer='json', request_method='GET')
    def launchconfigs_json(self):
        with boto_error_handler(self.request):
            launchconfigs_array = []
            launchconfigs_image_mapping = self.get_launchconfigs_image_mapping()
            scalinggroup_launchconfig_names = self.get_scalinggroups_launchconfig_names()
            for launchconfig in self.filter_items(self.items):
                security_groups = launchconfig.security_groups[0] if launchconfig.security_groups else [],
                image_id = launchconfig.image_id
                name = launchconfig.name
                launchconfigs_array.append(dict(
                    created_time=launchconfig.created_time.isoformat(),
                    image_id=image_id,
                    image_name=launchconfigs_image_mapping.get(image_id),
                    instance_monitoring=launchconfig.instance_monitoring.enabled == 'true',
                    key_name=launchconfig.key_name,
                    name=name,
                    security_groups=security_groups,
                    in_use=name in scalinggroup_launchconfig_names,
                ))
            return dict(results=launchconfigs_array)

    def get_items(self):
        return self.autoscale_conn.get_all_launch_configurations() if self.autoscale_conn else []

    def get_launchconfigs_image_mapping(self):
        launchconfigs_image_ids = [launchconfig.image_id for launchconfig in self.items]
        launchconfigs_images = self.ec2_conn.get_all_images(image_ids=launchconfigs_image_ids) if self.ec2_conn else []
        launchconfigs_image_mapping = dict()
        for image in launchconfigs_images:
            launchconfigs_image_mapping[image.id] = image.name or image.id
        return launchconfigs_image_mapping

    def get_scalinggroups_launchconfig_names(self):
        if self.autoscale_conn:
            return [group.launch_config_name for group in self.autoscale_conn.get_all_groups()]
        return []


class LaunchConfigView(BaseView):
    """Views for single LaunchConfig"""
    TEMPLATE = '../templates/launchconfigs/launchconfig_view.pt'

    def __init__(self, request):
        super(LaunchConfigView, self).__init__(request)
        self.ec2_conn = self.get_connection()
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        with boto_error_handler(request):
            self.launch_config = self.get_launch_config()
            self.image = self.get_image()
            self.security_groups = self.get_security_groups()
        self.delete_form = LaunchConfigDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            launch_config=self.launch_config,
            escaped_launch_config_name=quote(self.launch_config.name),
            in_use=self.is_in_use(),
            image=self.image,
            security_groups=self.security_groups,
            delete_form=self.delete_form,
        )

    @view_config(route_name='launchconfig_view', renderer=TEMPLATE)
    def launchconfig_view(self):
        return self.render_dict
 
    @view_config(route_name='launchconfig_delete', request_method='POST', renderer=TEMPLATE)
    def launchconfig_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            location = self.request.route_path('launchconfigs')
            prefix = _(u'Unable to delete launch configuration')
            template = '{0} {1} - {2}'.format(prefix, self.launch_config.name, '{0}')
            with boto_error_handler(self.request, location, template):
                self.log_request(_(u"Deleting launch configuration {0}").format(name))
                self.autoscale_conn.delete_launch_configuration(name)
                prefix = _(u'Successfully deleted launch configuration.')
                msg = '{0} {1}'.format(prefix, name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    def get_launch_config(self):
        if self.autoscale_conn:
            launch_config_param = self.request.matchdict.get('id')
            launch_configs = self.autoscale_conn.get_all_launch_configurations(names=[launch_config_param])
            return launch_configs[0] if launch_configs else None
        return None

    def get_image(self):
        if self.ec2_conn:
            images = self.ec2_conn.get_all_images(image_ids=[self.launch_config.image_id])
            image = images[0] if images else None
            image.platform = ImageView.get_platform(image)
            return image
        return None

    def get_security_groups(self):
        if self.ec2_conn:
            groupids = self.launch_config.security_groups
            security_groups = []
            if groupids:
                if groupids[0].startswith('sg-'):
                    security_groups = self.ec2_conn.get_all_security_groups(group_ids=groupids)
                else:
                    security_groups = self.ec2_conn.get_all_security_groups(groupnames=groupids)
            return security_groups
        return []

    def is_in_use(self):
        """Returns whether or not the launch config is in use (i.e. in any scaling group).
        :rtype: Boolean
        """
        launch_configs = []
        if self.autoscale_conn:
            launch_configs = [group.launch_config_name for group in self.autoscale_conn.get_all_groups()]
        return self.launch_config.name in launch_configs


class CreateLaunchConfigView(BlockDeviceMappingItemView):
    """Create Launch Configuration wizard"""
    TEMPLATE = '../templates/launchconfigs/launchconfig_wizard.pt'

    def __init__(self, request):
        super(CreateLaunchConfigView, self).__init__(request)
        self.request = request
        self.image = self.get_image()
        with boto_error_handler(request):
            self.securitygroups = self.get_security_groups()
        self.create_form = CreateLaunchConfigForm(
            self.request, image=self.image, conn=self.conn, securitygroups=self.securitygroups,
            formdata=self.request.params or None)
        self.filters_form = ImagesFiltersForm(
            self.request, cloud_type=self.cloud_type, formdata=self.request.params or None)
        self.keypair_form = KeyPairForm(self.request, formdata=self.request.params or None)
        self.securitygroup_form = SecurityGroupForm(self.request, formdata=self.request.params or None)
        self.generate_file_form = GenerateFileForm(self.request, formdata=self.request.params or None)
        self.securitygroups_rules_json = BaseView.escape_json(json.dumps(self.get_securitygroups_rules()))
        self.securitygroups_id_map_json = BaseView.escape_json(json.dumps(self.get_securitygroups_id_map()))
        self.images_json_endpoint = self.request.route_path('images_json')
        self.owner_choices = self.get_owner_choices()
        self.keypair_choices_json = BaseView.escape_json(json.dumps(dict(self.create_form.keypair.choices)))
        self.securitygroup_choices_json = BaseView.escape_json(json.dumps(dict(self.create_form.securitygroup.choices)))
        self.render_dict = dict(
            image=self.image,
            create_form=self.create_form,
            filters_form=self.filters_form,
            keypair_form=self.keypair_form,
            securitygroup_form=self.securitygroup_form,
            generate_file_form=self.generate_file_form,
            images_json_endpoint=self.images_json_endpoint,
            owner_choices=self.owner_choices,
            snapshot_choices=self.get_snapshot_choices(),
            securitygroups_rules_json=self.securitygroups_rules_json,
            securitygroups_id_map_json=self.securitygroups_id_map_json,
            keypair_choices_json=self.keypair_choices_json,
            securitygroup_choices_json=self.securitygroup_choices_json,
            security_group_names=[name for name, label in self.create_form.securitygroup.choices],
            preset='',
        )

    @view_config(route_name='launchconfig_new', renderer=TEMPLATE, request_method='GET')
    def launchconfig_new(self):
        """Displays the Create Launch Configuration wizard"""
        self.render_dict['preset'] = self.request.params.get('preset')
        return self.render_dict

    @view_config(route_name='launchconfig_create', renderer=TEMPLATE, request_method='POST')
    def launchconfig_create(self):
        """Handles the POST from the Create Launch Configuration wizard"""
        if self.create_form.validate():
            autoscale_conn = self.get_connection(conn_type='autoscale')
            location = self.request.route_path('launchconfigs')
            image_id = self.image.id
            name = self.request.params.get('name')
            key_name = self.request.params.get('keypair')
            if key_name and key_name == 'none':
                key_name = None  # Handle "None (advanced)" option
            securitygroup = self.request.params.get('securitygroup', 'default')
            security_groups = [securitygroup]  # Security group names
            instance_type = self.request.params.get('instance_type', 'm1.small')
            kernel_id = self.request.params.get('kernel_id') or None
            ramdisk_id = self.request.params.get('ramdisk_id') or None
            monitoring_enabled = self.request.params.get('monitoring_enabled') == 'y'
            bdmapping_json = self.request.params.get('block_device_mapping')
            block_device_mappings = [self.get_block_device_map(bdmapping_json)] if bdmapping_json != '{}' else None
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Creating launch configuration {0}").format(name))
                launch_config = LaunchConfiguration(
                    name=name,
                    image_id=image_id,
                    key_name=key_name,
                    security_groups=security_groups,
                    user_data=self.get_user_data(),
                    instance_type=instance_type,
                    kernel_id=kernel_id,
                    ramdisk_id=ramdisk_id,
                    block_device_mappings=block_device_mappings,
                    instance_monitoring=monitoring_enabled,
                )
                autoscale_conn.create_launch_configuration(launch_config=launch_config)
                msg = _(u'Successfully sent create launch configuration request. '
                        u'It may take a moment to create the launch configuration.')
                queue = Notification.SUCCESS
                self.request.session.flash(msg, queue=queue)

            if self.request.params.get('create_sg_from_lc') == 'y':
                escaped_name = quote(name)
                location = self.request.route_path('scalinggroup_new')+("?launch_config={0}".format(escaped_name))
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
        return self.render_dict

    def get_security_groups(self):
        if self.conn:
            return self.conn.get_all_security_groups()
        return []

    def get_securitygroups_rules(self):
        rules_dict = {}
        for security_group in self.securitygroups:
            if security_group.vpc_id is None:
                rules_dict[security_group.name] = SecurityGroupsView.get_rules(security_group.rules)
        return rules_dict

    def get_securitygroups_id_map(self):
        map_dict = {}
        for security_group in self.securitygroups:
            if security_group.vpc_id is None:
                map_dict[security_group.name] = security_group.id
        return map_dict
