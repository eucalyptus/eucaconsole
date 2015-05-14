# -*- coding: utf-8 -*-
# Copyright 2013-2014 Eucalyptus Systems, Inc.
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
Pyramid views for Eucalyptus and AWS elbs

"""
from urllib import quote
import simplejson as json
import time
import re

import boto.utils
from boto.ec2.elb import HealthCheck

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config

from ..i18n import _
from ..forms.elbs import (ELBForm, ELBDeleteForm, ELBsFiltersForm, CreateELBForm,
                          ELBInstancesFiltersForm, CertificateForm, BackendCertificateForm)
from ..models import Notification
from ..views import LandingPageView, BaseView, TaggedItemView, JSONResponse
from . import boto_error_handler


class ELBsView(LandingPageView):
    def __init__(self, request):
        super(ELBsView, self).__init__(request)
        self.request = request
        self.ec2_conn = self.get_connection(conn_type="ec2")
        self.elb_conn = self.get_connection(conn_type="elb")
        self.initial_sort_key = 'name'
        self.prefix = '/elbs'
        self.filter_keys = ['name', 'dns_name']
        self.sort_keys = self.get_sort_keys()
        self.json_items_endpoint = self.get_json_endpoint('elbs_json')
        self.delete_form = ELBDeleteForm(self.request, formdata=self.request.params or None)
        self.filters_form = ELBsFiltersForm(
            self.request, cloud_type=self.cloud_type, ec2_conn=self.ec2_conn, formdata=self.request.params or None)
        search_facets = self.filters_form.facets
        self.render_dict = dict(
            filter_keys=self.filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
            delete_form=self.delete_form,
        )

    @view_config(route_name='elbs', renderer='../templates/elbs/elbs.pt')
    def elbs_landing(self):
        # sort_keys are passed to sorting drop-down
        return self.render_dict

    @view_config(route_name='elbs_delete', request_method='POST')
    def elbs_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            location = self.request.route_path('elbs')
            prefix = _(u'Unable to delete elb')
            template = u'{0} {1} - {2}'.format(prefix, name, '{0}')
            with boto_error_handler(self.request, location, template):
                self.elb_conn.delete_load_balancer(name)
                prefix = _(u'Successfully deleted elb.')
                msg = u'{0} {1}'.format(prefix, name)
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
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='created_time', name=_(u'Creation time: Oldest to Newest')),
            dict(key='-created_time', name=_(u'Creation time: Newest to Oldest')),
            dict(key='image_name', name=_(u'Image Name: A to Z')),
            dict(key='-image_name', name=_(u'Image Name: Z to A')),
            dict(key='key_name', name=_(u'Key pair: A to Z')),
            dict(key='-key_name', name=_(u'Key pair: Z to A')),
        ]


class ELBsJsonView(LandingPageView):
    """JSON response view for ELB landing page"""
    def __init__(self, request):
        super(ELBsJsonView, self).__init__(request)
        self.ec2_conn = self.get_connection()
        self.elb_conn = self.get_connection(conn_type='elb')
        with boto_error_handler(request):
            self.items = self.get_items()
            self.securitygroups = self.get_all_security_groups()

    @view_config(route_name='elbs_json', renderer='json', request_method='POST')
    def elbs_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        with boto_error_handler(self.request):
            elbs_array = []
            for elb in self.filter_items(self.items):
                # boto doesn't convert elb created_time into dtobj like it does for others
                elb.created_time = boto.utils.parse_ts(elb.created_time)
                name = elb.name
                security_groups = self.get_security_groups(elb.security_groups)
                security_groups_array = sorted({
                    'name': group.name,
                    'id': group.id,
                    'rules_count': self.get_security_group_rules_count_by_id(group.id)
                    } for group in security_groups)
                elbs_array.append(dict(
                    created_time=self.dt_isoformat(elb.created_time),
                    in_use=False,
                    dns_name=elb.dns_name,
                    name=name,
                    security_groups=security_groups_array,
                ))
            return dict(results=elbs_array)

    def get_items(self):
        return self.elb_conn.get_all_load_balancers() if self.elb_conn else []

    def get_all_security_groups(self):
        if self.ec2_conn:
            return self.ec2_conn.get_all_security_groups()
        return []

    def get_security_groups(self, groupids):
        security_groups = []
        if groupids:
            for id in groupids:
                security_group = ''
                # Due to the issue that AWS-Classic and AWS-VPC different values,
                # name and id, for .securitygroup for launch config object
                if id.startswith('sg-'):
                    security_group = self.get_security_group_by_id(id)
                else:
                    security_group = self.get_security_group_by_name(id)
                if security_group:
                    security_groups.append(security_group)
        return security_groups

    def get_security_group_by_id(self, id):
        if self.securitygroups:
            for sgroup in self.securitygroups:
                if sgroup.id == id:
                    return sgroup
        return ''

    def get_security_group_by_name(self, name):
        if self.securitygroups:
            for sgroup in self.securitygroups:
                if sgroup.name == name:
                    return sgroup
        return ''

    def get_security_group_rules_count_by_id(self, id):
        if id.startswith('sg-'):
            security_group = self.get_security_group_by_id(id)
        else:
            security_group = self.get_security_group_by_name(id)
        if security_group:
            return len(security_group.rules)
        return None


class ConnectionSettingAttribute(object):
    """
    Represents the ConnectionSetting segment of ELB Attributes.
    """
    def __init__(self, connection=None):
        self.idle_timeout = None

    def __repr__(self):
        return 'ConnectionSettingAttribute(%s)' % (
            self.idle_timeout)

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 'IdleTimeout':
            self.idle_timeout = int(value)


# Current boto version 2.34.0 does not support ConnecitonSettingAttribute
class CustomLbAttributes(object):
    """
    Represents the Attributes of an Elastic Load Balancer.
    """
    def __init__(self, connection=None):
        self.connection = connection
        self.connecting_settings = ConnectionSettingAttribute(self.connection)

    def __repr__(self):
        return 'LbAttributes(%s)' % (
            repr(self.connecting_settings))

    def startElement(self, name, attrs, connection):
            return self.connecting_settings

    def endElement(self, name, value, connection):
        pass


class LbTagSet(dict):
    """
    A TagSet is used to collect the tags associated with a particular
    Load Balancer instance.
    """

    def __init__(self, connection=None):
        self.connection = connection
        self._current_key = None
        self._current_value = None
        self._tags_tag = False

    def startElement(self, name, attrs, connection):
        if name == 'Tags':
            self._tags_tag = True
        elif name == 'member' and self._tags_tag is True:
            self._current_key = None
            self._current_value = None

    def endElement(self, name, value, connection):
        if name == 'Key':
            self._current_key = value
        elif name == 'Value':
            self._current_value = value
        elif name == 'member' and self._tags_tag is True:
            self[self._current_key] = self._current_value
        elif name == 'Tags':
            self._tags_tag = False


class BaseELBView(TaggedItemView):
    """Views for single ELB"""
    TEMPLATE = '../templates/elbs/elb_view.pt'

    def __init__(self, request):
        super(BaseELBView, self).__init__(request)
        self.request = request
        self.ec2_conn = self.get_connection()
        self.iam_conn = self.get_connection(conn_type='iam')
        self.elb_conn = self.get_connection(conn_type='elb')
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.is_vpc_supported = BaseView.is_vpc_supported(request)

    def get_listeners_args(self):
        listeners_json = self.request.params.get('elb_listener')
        listeners = json.loads(listeners_json) if listeners_json else []
        listeners_args = []
        for listener in listeners:
            from_protocol = listener.get('fromProtocol')
            from_port = listener.get('fromPort')
            to_protocol = listener.get('toProtocol')
            to_port = listener.get('toPort')
            certificate_arn = listener.get('certificateARN') or None
            if certificate_arn is not None:
                listeners_args.append((from_port, to_port, from_protocol, to_protocol, certificate_arn))
            else:
                listeners_args.append((from_port, to_port, from_protocol, to_protocol))
        return listeners_args

    def handle_configure_health_check(self, name):
        ping_protocol = self.request.params.get('ping_protocol')
        ping_port = self.request.params.get('ping_port')
        ping_path = self.request.params.get('ping_path')
        response_timeout = self.request.params.get('response_timeout')
        time_between_pings = self.request.params.get('time_between_pings')
        failures_until_unhealthy = self.request.params.get('failures_until_unhealthy')
        passes_until_healthy = self.request.params.get('passes_until_healthy')
        ping_target = u"{0}:{1}".format(ping_protocol, ping_port)
        if ping_protocol in ['HTTP', 'HTTPS']:
            ping_target = u"{0}/{1}".format(ping_target, ping_path)
        hc = HealthCheck(
            timeout=response_timeout,
            interval=time_between_pings,
            healthy_threshold=passes_until_healthy,
            unhealthy_threshold=failures_until_unhealthy,
            target=ping_target
        )
        self.elb_conn.configure_health_check(name, hc)

    def get_instance_selector_text(self):
        instance_selector_text = {'name': _(u'NAME (ID)'), 'tags': _(u'TAGS'),
                                  'zone': _(u'AVAILABILITY ZONE'), 'subnet': _(u'VPC SUBNET'), 'status': _(u'STATUS'),
                                  'no_matching_instance_error_msg': _(u'No matching instances')}
        return instance_selector_text

    def get_protocol_list(self):
        protocol_list = ()
        if self.cloud_type == 'aws':
            protocol_list = ({'name': 'HTTP', 'value': 'HTTP', 'port': '80'},
                             {'name': 'TCP', 'value': 'TCP', 'port': '80'})
        else:
            protocol_list = ({'name': 'HTTP', 'value': 'HTTP', 'port': '80'},
                             {'name': 'HTTPS', 'value': 'HTTPS', 'port': '443'},
                             {'name': 'TCP', 'value': 'TCP', 'port': '80'},
                             {'name': 'SSL', 'value': 'SSL', 'port': '443'})
        return protocol_list

    def get_default_vpc_network(self):
        default_vpc = self.request.session.get('default_vpc', [])
        if self.is_vpc_supported:
            if 'none' in default_vpc or 'None' in default_vpc:
                if self.cloud_type == 'aws':
                    return 'None'
                # for euca, return the first vpc on the list
                if self.vpc_conn:
                    with boto_error_handler(self.request):
                        vpc_networks = self.vpc_conn.get_all_vpcs()
                        if vpc_networks:
                            return vpc_networks[0].id
            else:
                return default_vpc[0]
        return 'None'

    def get_vpc_subnets(self):
        subnets = []
        if self.vpc_conn:
            with boto_error_handler(self.request):
                vpc_subnets = self.vpc_conn.get_all_subnets()
                for vpc_subnet in vpc_subnets:
                    subnet_string = u'{0} ({1}) | {2}'.format(vpc_subnet.cidr_block,
                                                              vpc_subnet.id, vpc_subnet.availability_zone)
                    subnets.append(dict(
                        id=vpc_subnet.id,
                        name=subnet_string,
                        vpc_id=vpc_subnet.vpc_id,
                        availability_zone=vpc_subnet.availability_zone,
                        state=vpc_subnet.state,
                        cidr_block=vpc_subnet.cidr_block,
                    ))
        return subnets

    def get_availability_zones(self):
        availability_zones = []
        if self.ec2_conn:
            with boto_error_handler(self.request):
                zones = self.ec2_conn.get_all_zones()
                for zone in zones:
                    availability_zones.append(dict(id=zone.name, name=zone.name))
        return availability_zones

    def add_elb_tags(self, elb_name):
        tags_json = self.request.params.get('tags')
        tags_dict = json.loads(tags_json) if tags_json else {}
        add_tags_params = {'LoadBalancerNames.member.1': elb_name}
        index = 1
        for key, value in tags_dict.items():
            key = self.unescape_braces(key.strip())
            if not any([key.startswith('aws:'), key.startswith('euca:')]):
                add_tags_params['Tags.member.%d.Key' % index] = key
                add_tags_params['Tags.member.%d.Value' % index] = self.unescape_braces(value.strip())
                index += 1
        if index > 1:
            self.elb_conn.get_status('AddTags', add_tags_params)


class ELBView(BaseELBView):
    """Views for single ELB"""
    TEMPLATE = '../templates/elbs/elb_view.pt'

    def __init__(self, request):
        super(ELBView, self).__init__(request)
        with boto_error_handler(request):
            self.elb = self.get_elb()
            # boto doesn't convert elb created_time into dtobj like it does for others
            if self.elb:
                self.elb.created_time = boto.utils.parse_ts(self.elb.created_time)
                self.elb.idle_timeout = self.get_elb_attribute_idle_timeout()
                self.get_health_check_data()
                tags_params = {'LoadBalancerNames.member.1': self.elb.name}
                self.elb.tags = self.elb_conn.get_object('DescribeTags', tags_params, LbTagSet)
            else:
                raise HTTPNotFound()
        self.elb_form = ELBForm(
            self.request, conn=self.ec2_conn, vpc_conn=self.vpc_conn,
            elb=self.elb, securitygroups=self.get_security_groups(),
            formdata=self.request.params or None)
        self.delete_form = ELBDeleteForm(self.request, formdata=self.request.params or None)
        filter_keys = ['id', 'name', 'placement', 'state', 'tags', 'vpc_subnet_display', 'vpc_name']
        filters_form = ELBInstancesFiltersForm(
            self.request, ec2_conn=self.ec2_conn, autoscale_conn=self.autoscale_conn,
            iam_conn=None, vpc_conn=self.vpc_conn,
            cloud_type=self.cloud_type, formdata=self.request.params or None)
        search_facets = filters_form.facets
        self.render_dict = dict(
            elb=self.elb,
            elb_name=self.escape_braces(self.elb.name) if self.elb else '',
            elb_created_time=self.dt_isoformat(self.elb.created_time) if self.elb else '',
            escaped_elb_name=quote(self.elb.name) if self.elb else '',
            elb_tags=TaggedItemView.get_tags_display(self.elb.tags) if self.elb.tags else '',
            elb_form=self.elb_form,
            delete_form=self.delete_form,
            in_use=False,
            protocol_list=self.get_protocol_list(),
            listener_list=self.get_listener_list(),
            is_vpc_supported=self.is_vpc_supported,
            elb_vpc_network=self.get_vpc_network_name(),
            security_group_placeholder_text=_(u'Select...'),
            filter_keys=filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='elb_view', renderer=TEMPLATE)
    def elb_view(self):
        self.__init__(self.request)
        return self.render_dict

    @view_config(route_name='elb_update', request_method='POST', renderer=TEMPLATE)
    def elb_update(self):
        if self.elb_form.validate():
            idle_timeout = self.request.params.get('idle_timeout')
            elb_listener = self.request.params.get('elb_listener')
            securitygroup = self.request.params.getall('securitygroup') or None
            listeners_args = self.get_listeners_args()
            vpc_subnet = self.request.params.getall('vpc_subnet') or None
            if vpc_subnet == 'None':
                vpc_subnet = None
            zone = self.request.params.getall('zone') or None
            cross_zone_enabled = self.request.params.get('cross_zone_enabled') or False
            instances = self.request.params.getall('instances') or None
            location = self.request.route_path('elb_view', id=self.elb.name)
            current_tab = self.request.params.get('current_tab') or None
            if current_tab:
                location = '{0}?tab={1}'.format(location, current_tab)
            prefix = _(u'Unable to update load balancer')
            template = u'{0} {1} - {2}'.format(prefix, self.elb.name, '{0}')
            with boto_error_handler(self.request, location, template):
                self.update_elb_idle_timeout(self.elb.name, idle_timeout)
                self.update_load_balancer_listeners(self.elb.name, listeners_args)
                self.update_elb_tags(self.elb.name)
                if vpc_subnet is None:
                    self.update_elb_zones(self.elb.name, self.elb.availability_zones, zone)
                    if cross_zone_enabled == 'on':
                        self.elb_conn.modify_lb_attribute(self.elb.name, 'crossZoneLoadBalancing', True)
                    else:
                        self.elb_conn.modify_lb_attribute(self.elb.name, 'crossZoneLoadBalancing', False)
                else:
                    if self.elb.security_groups != securitygroup:
                        self.elb_conn.apply_security_groups_to_lb(self.elb.name, securitygroup)
                    self.update_elb_subnets(self.elb.name, self.elb.subnets, vpc_subnet)
                self.update_elb_instances(self.elb.name, self.elb.instances, instances)
                self.handle_configure_health_check(self.elb.name)
                msg = _(u"Updating load balancer")
                self.log_request(u"{0} {1}".format(msg, self.elb.name))
                prefix = _(u'Successfully updated load balancer.')
                msg = u'{0} {1}'.format(prefix, self.elb.name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.elb_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='elb_delete', request_method='POST', renderer=TEMPLATE)
    def elb_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            location = self.request.route_path('elbs')
            prefix = _(u'Unable to delete elb')
            template = u'{0} {1} - {2}'.format(prefix, self.elb.name, '{0}')
            with boto_error_handler(self.request, location, template):
                msg = _(u"Deleting elb")
                self.log_request(u"{0} {1}".format(msg, name))
                self.elb_conn.delete_load_balancer(name)
                prefix = _(u'Successfully deleted elb.')
                msg = u'{0} {1}'.format(prefix, name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    def get_elb(self):
        if self.elb_conn:
            elb_param = self.request.matchdict.get('id')
            elbs = self.elb_conn.get_all_load_balancers(load_balancer_names=[elb_param])
            return elbs[0] if elbs else None
        return None

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'resource_name': 'elb',
            'is_vpc_supported': self.is_vpc_supported,
            'default_vpc_network': self.get_default_vpc_network(),
            'availability_zones': self.elb.availability_zones if self.elb else [],
            'availability_zone_choices': self.get_availability_zones(),
            'vpc_subnet_choices': self.get_vpc_subnets(),
            'elb_vpc_network': self.elb.vpc_id if self.elb else [],
            'elb_vpc_subnets': self.elb.subnets if self.elb else [],
            'instance_selector_text': self.get_instance_selector_text(),
            'all_instances': self.get_all_instances(),
            'elb_instance_health': self.get_elb_instance_health(),
            'is_cross_zone_enabled': self.get_elb_cross_zone_load_balancing(),
            'securitygroups': self.elb.security_groups if self.elb else [],
            'securitygroups_json_endpoint': self.request.route_path('securitygroups_json'),
            'instances': self.get_elb_instance_list(),
            'instances_json_endpoint': self.request.route_path('instances_json'),
            'health_check_ping_protocol': self.elb.ping_protocol if self.elb else '',
            'health_check_ping_port': self.elb.ping_port if self.elb else '',
            'health_check_ping_path': self.elb.ping_path if self.elb else '',
            'health_check_interval': self.elb.health_check.interval if self.elb else '',
            'health_check_timeout': self.elb.health_check.timeout if self.elb else '',
            'health_check_healthy_threshold': self.elb.health_check.healthy_threshold if self.elb else '',
            'health_check_unhealthy_threshold': self.elb.health_check.unhealthy_threshold if self.elb else '',
        }))

    def get_elb_attribute_idle_timeout(self):
        if self.elb:
            params = {'LoadBalancerName': self.elb.name}
            elb_attrs = self.elb_conn.get_object('DescribeLoadBalancerAttributes',
                                                 params, CustomLbAttributes)
            if elb_attrs:
                return elb_attrs.connecting_settings.idle_timeout

    def update_elb_idle_timeout(self, elb_name, idle_timeout):
        if self.elb_conn:
            params = {'LoadBalancerName': elb_name}
            params['LoadBalancerAttributes.ConnectionSettings.IdleTimeout'] = idle_timeout
            self.elb_conn.get_status('ModifyLoadBalancerAttributes', params, verb='GET')

    def get_listener_list(self):
        listener_list = []
        if self.elb and self.elb.listeners:
            for listener_obj in self.elb.listeners:
                listener = listener_obj.get_tuple()
                listener_list.append({'from_port': listener[0],
                                      'to_port': listener[1],
                                      'protocol': listener[2]})
        return listener_list

    def update_load_balancer_listeners(self, name, listeners_args):
        if self.elb_conn and self.elb:
            ports = []
            if self.elb.listeners:
                for listener_obj in self.elb.listeners:
                    listener = listener_obj.get_tuple()
                    ports.append(listener[0])
                if ports:
                    self.elb_conn.delete_load_balancer_listeners(name, ports)
                    # sleep is needed for Eucalyptus to avoid not finding the elb error
                    time.sleep(1)
            self.elb_conn.create_load_balancer_listeners(name, listeners=listeners_args)

    def update_elb_tags(self, elb_name):
        if elb_name:
            self.remove_all_elb_tags(elb_name)
            self.add_elb_tags(elb_name)

    def remove_all_elb_tags(self, elb_name):
        if self.elb.tags:
            remove_tags_params = {'LoadBalancerNames.member.1': elb_name}
            index = 1
            for tag in self.elb.tags.items():
                key = self.unescape_braces(tag[0].strip())
                if not any([key.startswith('aws:'), key.startswith('euca:')]):
                    remove_tags_params['Tags.member.%d.Key' % index] = key
                    index += 1
            if index > 1:
                self.elb_conn.get_status('RemoveTags', remove_tags_params, verb='POST')

    def update_elb_zones(self, elb_name, prev_zones, new_zones):
        if prev_zones and new_zones:
            add_zones = []
            remove_zones = []
            for prev_zone in prev_zones:
                exists_zone = False
                for new_zone in new_zones:
                    if prev_zone == new_zone:
                        exists_zone = True
                if exists_zone is False:
                    remove_zones.append(prev_zone)
            for new_zone in new_zones:
                exists_zone = False
                for prev_zone in prev_zones:
                    if prev_zone == new_zone:
                        exists_zone = True
                if exists_zone is False:
                    add_zones.append(new_zone)
            if remove_zones:
                self.elb_conn.disable_availability_zones(elb_name, remove_zones)
            if add_zones:
                self.elb_conn.enable_availability_zones(elb_name, add_zones)

    def update_elb_subnets(self, elb_name, prev_subnets, new_subnets):
        if prev_subnets and new_subnets:
            add_subnets = []
            remove_subnets = []
            for prev_subnet in prev_subnets:
                exists_subnet = False
                for new_subnet in new_subnets:
                    if prev_subnet == new_subnet:
                        exists_subnet = True
                if exists_subnet is False:
                    remove_subnets.append(prev_subnet)
            for new_subnet in new_subnets:
                exists_subnet = False
                for prev_subnet in prev_subnets:
                    if prev_subnet == new_subnet:
                        exists_subnet = True
                if exists_subnet is False:
                    add_subnets.append(new_subnet)
            if remove_subnets:
                self.elb_conn.detach_lb_from_subnets(elb_name, remove_subnets)
            if add_subnets:
                self.elb_conn.attach_lb_to_subnets(elb_name, add_subnets)

    def update_elb_instances(self, elb_name, prev_instances, new_instances):
        add_instances = []
        remove_instances = []
        if prev_instances and new_instances:
            for prev_instance in prev_instances:
                exists_instance = False
                for new_instance in new_instances:
                    if prev_instance.id == new_instance:
                        exists_instance = True
                if exists_instance is False:
                    remove_instances.append(prev_instance.id)
            for new_instance in new_instances:
                exists_instance = False
                for prev_instance in prev_instances:
                    if prev_instance.id == new_instance:
                        exists_instance = True
                if exists_instance is False:
                    add_instances.append(new_instance)
        else:
            if prev_instances:
                for prev_instance in prev_instances:
                    remove_instances.append(prev_instance.id)
            if new_instances:
                for new_instance in new_instances:
                    add_instances.append(new_instance)
        if remove_instances:
            self.elb_conn.deregister_instances(elb_name, remove_instances)
        if add_instances:
            self.elb_conn.register_instances(elb_name, add_instances)

    def get_vpc_network_name(self):
        if self.is_vpc_supported:
            if self.elb.vpc_id and self.vpc_conn:
                with boto_error_handler(self.request):
                    vpc_networks = self.vpc_conn.get_all_vpcs(vpc_ids=self.elb.vpc_id)
                    if vpc_networks:
                        vpc_name = TaggedItemView.get_display_name(vpc_networks[0])
                        return vpc_name
        return 'None'

    def get_security_groups(self):
        securitygroups = []
        if self.elb and self.elb.vpc_id:
            with boto_error_handler(self.request):
                securitygroups = self.ec2_conn.get_all_security_groups(filters={'vpc-id': [self.elb.vpc_id]})
        return securitygroups

    def get_elb_instance_list(self):
        instances = []
        if self.elb and self.elb.instances:
            for instance in self.elb.instances:
                if instance:
                    instances.append(instance.id)
        return instances

    def get_all_instances(self):
        if self.ec2_conn:
            instances = []
            for reservation in self.ec2_conn.get_all_reservations():
                for instance in reservation.instances:
                    instances.append(dict(
                        id=instance.id,
                        vpc_id=instance.vpc_id,
                        subnet_id=instance.subnet_id,
                        zone=instance._placement.zone,
                    ))
        return instances

    def get_elb_instance_health(self):
        if self.elb_conn and self.elb:
            instance_health = []
            instances = self.elb_conn.describe_instance_health(self.elb.name)
            for instance in instances:
                instance_health.append(dict(
                    instance_id=instance.instance_id,
                    state=instance.state,
                ))
        return instance_health

    def get_health_check_data(self):
        if self.elb is not None and self.elb.health_check.target is not None:
            self.elb.ping_protocol = ''
            self.elb.ping_port = ''
            self.elb.ping_path = ''
            match = re.search('^(\w+):(\d+)\/?(.+)?', self.elb.health_check.target)
            if match:
                self.elb.ping_protocol = match.group(1)
                self.elb.ping_port = match.group(2)
                if match.group(3) is not None:
                    self.elb.ping_path = match.group(3)

    def get_elb_cross_zone_load_balancing(self):
        if self.elb_conn and self.elb:
            is_cross_zone_enabled = self.elb.is_cross_zone_load_balancing()
        return is_cross_zone_enabled


class CreateELBView(BaseELBView):
    """Create ELB wizard"""
    TEMPLATE = '../templates/elbs/elb_wizard.pt'

    def __init__(self, request):
        super(CreateELBView, self).__init__(request)
        self.create_form = CreateELBForm(
            self.request, conn=self.ec2_conn, vpc_conn=self.vpc_conn, formdata=self.request.params or None)
        self.certificate_form = CertificateForm(self.request, conn=self.ec2_conn,
                                                iam_conn=self.iam_conn, elb_conn=self.elb_conn,
                                                formdata=self.request.params or None)
        self.backend_certificate_form = BackendCertificateForm(self.request, conn=self.ec2_conn,
                                                               iam_conn=self.iam_conn, elb_conn=self.elb_conn,
                                                               formdata=self.request.params or None)
        filter_keys = ['id', 'name', 'placement', 'state', 'security_groups', 'vpc_subnet_display', 'vpc_name']
        filters_form = ELBInstancesFiltersForm(
            self.request, ec2_conn=self.ec2_conn, autoscale_conn=self.autoscale_conn,
            iam_conn=None, vpc_conn=self.vpc_conn,
            cloud_type=self.cloud_type, formdata=self.request.params or None)
        search_facets = filters_form.facets
        self.render_dict = dict(
            create_form=self.create_form,
            certificate_form=self.certificate_form,
            backend_certificate_form=self.backend_certificate_form,
            protocol_list=self.get_protocol_list(),
            security_group_placeholder_text=_(u'Select...'),
            is_vpc_supported=self.is_vpc_supported,
            avail_zones_placeholder_text=_(u'Select availability zones'),
            vpc_subnets_placeholder_text=_(u'Select VPC subnets'),
            filter_keys=filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='elb_new', renderer=TEMPLATE)
    def elb_view(self):
        return self.render_dict

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'resource_name': 'elb',
            'wizard_tab_list': self.get_wizard_tab_list(),
            'is_vpc_supported': self.is_vpc_supported,
            'default_vpc_network': self.get_default_vpc_network(),
            'availability_zone_choices': self.get_availability_zones(),
            'vpc_subnet_choices': self.get_vpc_subnets(),
            'instance_selector_text': self.get_instance_selector_text(),
            'securitygroups_json_endpoint': self.request.route_path('securitygroups_json'),
            'instances_json_endpoint': self.request.route_path('instances_json'),
        }))

    def get_wizard_tab_list(self):
        if self.cloud_type == 'aws' or self.is_vpc_supported:
            tab_list = ({'title': _(u'General'), 'render': True, 'display_id': 1},
                        {'title': _(u'Network'), 'render': True, 'display_id': 2},
                        {'title': _(u'Instances'), 'render': True, 'display_id': 3},
                        {'title': _(u'Health Check & Advanced'), 'render': True, 'display_id': 4})
        else:
            tab_list = ({'title': _(u'General'), 'render': True, 'display_id': 1},
                        {'title': _(u'Network'), 'render': False, 'display_id': ''},
                        {'title': _(u'Instances'), 'render': True, 'display_id': 2},
                        {'title': _(u'Health Check & Advanced'), 'render': True, 'display_id': 3})
        return tab_list

    @view_config(route_name='elb_create', request_method='POST', renderer=TEMPLATE)
    def elb_create(self):
        # Ignore the security group requirement in case on Non-VPC system
        vpc_network = self.request.params.get('vpc_network') or None
        if vpc_network == 'None':
            vpc_network = None
        if vpc_network is None:
            del self.create_form.securitygroup
        if self.create_form.validate():
            name = self.request.params.get('name')
            elb_listener = self.request.params.get('elb_listener')
            certificate_arn = self.request.params.get('certificate_arn') or None
            listeners_args = self.get_listeners_args()
            vpc_subnet = self.request.params.getall('vpc_subnet') or None
            if vpc_subnet == 'None':
                vpc_subnet = None
            securitygroup = self.request.params.getall('securitygroup') or None
            zone = self.request.params.getall('zone') or None
            cross_zone_enabled = self.request.params.get('cross_zone_enabled') or False
            instances = self.request.params.getall('instances') or None
            backend_certificates = self.request.params.get('backend_certificates') or None
            with boto_error_handler(self.request, self.request.route_path('elbs')):
                self.log_request(_(u"Creating elastic load balancer {0}").format(name))
                if vpc_subnet is None:
                    params = dict(complex_listeners=listeners_args)
                    self.elb_conn.create_load_balancer(name, zone, **params)
                    self.elb_conn.enable_availability_zones(name, zone)
                else:
                    params = dict(subnets=vpc_subnet,
                                  security_groups=securitygroup,
                                  complex_listeners=listeners_args)
                    self.elb_conn.create_load_balancer(name, None, **params)
                self.handle_configure_health_check(name)
                if instances is not None:
                    self.elb_conn.register_instances(name, instances)
                if cross_zone_enabled == 'y':
                    self.elb_conn.modify_lb_attribute(name, 'crossZoneLoadBalancing', True)
                if backend_certificates is not None and backend_certificates != '[]':
                    self.handle_backend_certificate_create(name)
                self.add_elb_tags(name)
                prefix = _(u'Successfully created elastic load balancer')
                msg = u'{0} {1}'.format(prefix, name)
                location = self.request.route_path('elbs')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
            return self.render_dict

    @view_config(route_name='certificate_create', request_method='POST', renderer=TEMPLATE)
    def certificate_create(self):
        if self.certificate_form.validate():
            certificate_name = self.request.params.get('certificate_name')
            private_key = self.request.params.get('private_key')
            public_key_certificate = self.request.params.get('public_key_certificate')
            certificate_chain = self.request.params.get('certificate_chain') or None
            with boto_error_handler(self.request):
                certificate_result = self.iam_conn.upload_server_cert(certificate_name, public_key_certificate,
                                                                      private_key, cert_chain=certificate_chain,
                                                                      path=None)
                prefix = _(u'Successfully uploaded server certificate')
                msg = u'{0} {1}'.format(prefix, certificate_name)
                certificate_arn = certificate_result.upload_server_certificate_result.server_certificate_metadata.arn
                return JSONResponse(status=200, message=msg, id=certificate_arn)
        else:
            form_errors = ', '.join(self.certificate_form.get_errors_list())
            return JSONResponse(status=400, message=form_errors)  # Validation failure = bad request

    def handle_backend_certificate_create(self, elb_name):
        backend_certificates_json = self.request.params.get('backend_certificates')
        backend_certificates = json.loads(backend_certificates_json) if backend_certificates_json else []
        public_policy_attributes = dict()
        public_policy_type = u'PublicKeyPolicyType'
        backend_policy_type = u'BackendServerAuthenticationPolicyType'
        backend_policy_name = u'BackendPolicy-{0}'.format(elb_name)
        backend_policy_params = {'LoadBalancerName': elb_name,
                                 'PolicyName': backend_policy_name,
                                 'PolicyTypeName': backend_policy_type}
        index = 1
        for cert in backend_certificates:
            public_policy_name = u'EucaConsole-PublicKeyPolicy-{0}'.format(cert.get('name'))
            public_policy_attributes['PublicKey'] = cert.get('certificateBody')
            self.elb_conn.create_lb_policy(elb_name, public_policy_name, public_policy_type, public_policy_attributes)
            backend_policy_params['PolicyAttributes.member.%d.AttributeName' % index] = 'PublicKeyPolicyName'
            backend_policy_params['PolicyAttributes.member.%d.AttributeValue' % index] = public_policy_name
            index += 1
        self.elb_conn.get_status('CreateLoadBalancerPolicy', backend_policy_params)
        # sleep is needed for the previous policy creation to complete
        time.sleep(1)
        instance_port = 443
        self.elb_conn.set_lb_policies_of_backend_server(elb_name, instance_port, backend_policy_name)
