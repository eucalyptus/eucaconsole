# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS launch configurations

"""
import re

from boto.exception import EC2ResponseError

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.launchconfigs import LaunchConfigDeleteForm
from ..models import Notification
from ..views import LandingPageView, BaseView


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



