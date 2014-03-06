# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS launch configurations

"""
import re
import simplejson as json

from boto.ec2.autoscale.launchconfig import LaunchConfiguration
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config
import time

from ..forms import GenerateFileForm
from ..forms.keypairs import KeyPairForm
from ..forms.launchconfigs import LaunchConfigDeleteForm, CreateLaunchConfigForm
from ..forms.securitygroups import SecurityGroupForm
from ..models import Notification
from ..views import LandingPageView, BaseView, BlockDeviceMappingItemView
from ..views.images import ImageView
from ..views.securitygroups import SecurityGroupsView


class LaunchConfigsView(LandingPageView):
    def __init__(self, request):
        super(LaunchConfigsView, self).__init__(request)
        self.request = request
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.initial_sort_key = 'name'
        self.prefix = '/launchconfigs'
        self.filter_keys = ['image_id', 'image_name', 'key_name', 'name', 'security_groups']
        self.sort_keys = self.get_sort_keys()
        self.json_items_endpoint = self.request.route_url('launchconfigs_json')
        self.delete_form = LaunchConfigDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            filter_fields=self.filter_fields,
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
            try:
                self.autoscale_conn.delete_launch_configuration(name)
                prefix = _(u'Successfully deleted launch configuration.')
                msg = '{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                prefix = _(u'Unable to delete launch configuration')
                msg = '{0} {1} - {2}'.format(prefix, name, err.message)
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            location = self.request.route_url('launchconfigs')
            return HTTPFound(location=location)
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


class LaunchConfigsJsonView(BaseView):
    """JSON response view for Launch Configurations landing page"""
    def __init__(self, request):
        super(LaunchConfigsJsonView, self).__init__(request)
        self.ec2_conn = self.get_connection()
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.launch_configs = self.autoscale_conn.get_all_launch_configurations() if self.autoscale_conn else []

    @view_config(route_name='launchconfigs_json', renderer='json', request_method='GET')
    def launchconfigs_json(self):
        launchconfigs_array = []
        launchconfigs_image_mapping = self.get_launchconfigs_image_mapping()
        scalinggroup_launchconfig_names = self.get_scalinggroups_launchconfig_names()
        for launchconfig in self.launch_configs:
            security_groups = self.get_launchconfig_security_groups(launchconfig)
            image_id = launchconfig.image_id
            name=launchconfig.name
            launchconfigs_array.append(dict(
                created_time=launchconfig.created_time.isoformat(),
                image_id=image_id,
                image_name=launchconfigs_image_mapping.get(image_id),
                instance_monitoring='monitored' if bool(launchconfig.instance_monitoring) else 'unmonitored',
                key_name=launchconfig.key_name,
                name=name,
                security_groups=security_groups,
                in_use=name in scalinggroup_launchconfig_names,
            ))
        return dict(results=launchconfigs_array)

    def get_launchconfigs_image_mapping(self):
        launchconfigs_image_ids = [launchconfig.image_id for launchconfig in self.launch_configs]
        launchconfigs_images = self.ec2_conn.get_all_images(image_ids=launchconfigs_image_ids) if self.ec2_conn else []
        launchconfigs_image_mapping = dict()
        for image in launchconfigs_images:
            launchconfigs_image_mapping[image.id] = image.name or image.id
        return launchconfigs_image_mapping

    def get_scalinggroups_launchconfig_names(self):
        if self.autoscale_conn:
            return [group.launch_config_name for group in self.autoscale_conn.get_all_groups()]
        return []

    def get_launchconfig_security_groups(self, launch_config):
        if self.ec2_conn:
            groupids = launch_config.security_groups
            security_groups = []
            sgroup_name_map_array = []
            if groupids[0][:3] == "sg-":
                security_groups = self.ec2_conn.get_all_security_groups(group_ids=groupids)
            else:
                security_groups = self.ec2_conn.get_all_security_groups(groupnames=groupids)
            for sgroup in security_groups:
                sgroup_name_map_array.append(dict(id=sgroup.id, name=sgroup.name or sgroup.id))
            return sgroup_name_map_array
        return []

class LaunchConfigView(BaseView):
    """Views for single LaunchConfig"""
    TEMPLATE = '../templates/launchconfigs/launchconfig_view.pt'

    def __init__(self, request):
        super(LaunchConfigView, self).__init__(request)
        self.ec2_conn = self.get_connection()
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.launch_config = self.get_launch_config()
        self.image = self.get_image()
        self.security_groups = self.get_security_groups()
        self.delete_form = LaunchConfigDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            launch_config=self.launch_config,
            in_use=self.is_in_use(),
            image=self.image,
            security_groups=self.security_groups,
            delete_form=self.delete_form,
        )

    @view_config(route_name='launchconfig_view', renderer=TEMPLATE)
    def launchconfig_view(self):
        self.launch_config.instance_monitoring_boolean = re.match(
            r'InstanceMonitoring\((\w+)\)', str(self.launch_config.instance_monitoring)).group(1)
        return self.render_dict
 
    @view_config(route_name='launchconfig_delete', request_method='POST', renderer=TEMPLATE)
    def launchconfig_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            try:
                self.autoscale_conn.delete_launch_configuration(name)
                prefix = _(u'Successfully deleted launch configuration.')
                msg = '{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                prefix = _(u'Unable to delete launch configuration')
                msg = '{0} {1} - {2}'.format(prefix, self.launch_config.name, err.message)
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            location = self.request.route_url('launchconfigs')
            return HTTPFound(location=location)
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
            if groupids[0][:3] == "sg-":
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
        self.securitygroups = self.get_security_groups()
        self.create_form = CreateLaunchConfigForm(
            self.request, image=self.image, conn=self.conn, securitygroups=self.securitygroups,
            formdata=self.request.params or None)
        self.keypair_form = KeyPairForm(self.request, formdata=self.request.params or None)
        self.securitygroup_form = SecurityGroupForm(self.request, formdata=self.request.params or None)
        self.generate_file_form = GenerateFileForm(self.request, formdata=self.request.params or None)
        self.securitygroups_rules_json = json.dumps(self.get_securitygroups_rules())
        self.images_json_endpoint = self.request.route_url('images_json')
        self.securitygroups_rules_json = json.dumps(self.get_securitygroups_rules())
        self.owner_choices = self.get_owner_choices()
        self.keypair_choices_json = json.dumps(dict(self.create_form.keypair.choices))
        self.securitygroup_choices_json = json.dumps(dict(self.create_form.securitygroup.choices))
        self.render_dict = dict(
            image=self.image,
            create_form=self.create_form,
            keypair_form=self.keypair_form,
            securitygroup_form=self.securitygroup_form,
            generate_file_form=self.generate_file_form,
            images_json_endpoint=self.images_json_endpoint,
            owner_choices=self.owner_choices,
            snapshot_choices=self.get_snapshot_choices(),
            securitygroups_rules_json=self.securitygroups_rules_json,
            keypair_choices_json=self.keypair_choices_json,
            securitygroup_choices_json=self.securitygroup_choices_json,
            security_group_names=[name for name, label in self.create_form.securitygroup.choices],
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
            kernel_id = self.request.params.get('kernel_id') or None
            ramdisk_id = self.request.params.get('ramdisk_id') or None
            monitoring_enabled = self.request.params.get('monitoring_enabled', False)
            bdmapping_json = self.request.params.get('block_device_mapping')
            block_device_mappings = [self.get_block_device_map(bdmapping_json)] if bdmapping_json else None
            try:
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
                time.sleep(2)
                msg = _(u'Successfully sent create launch configuration request. '
                        u'It may take a moment to create the launch configuration.')
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    def get_security_groups(self):
        if self.conn:
            return self.conn.get_all_security_groups()
        return []

    def get_securitygroups_rules(self):
        rules_dict = {}
        for security_group in self.securitygroups:
            rules_dict[security_group.name] = SecurityGroupsView.get_rules(security_group.rules)
        return rules_dict
