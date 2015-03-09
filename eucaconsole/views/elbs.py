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

import boto.utils
from boto.ec2.elb import HealthCheck

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..i18n import _
from ..forms.elbs import ELBDeleteForm, ELBsFiltersForm, CreateELBForm, ELBInstancesFiltersForm, CertificateForm 
from ..models import Notification
from ..views import LandingPageView, BaseView, JSONResponse
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
            filter_fields=False,
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

class ELBView(BaseView):
    """Views for single ELB"""
    TEMPLATE = '../templates/elbs/elb_view.pt'

    def __init__(self, request):
        super(ELBView, self).__init__(request)
        self.ec2_conn = self.get_connection()
        self.elb_conn = self.get_connection(conn_type='elb')
        with boto_error_handler(request):
            self.elb = self.get_elb()
            # boto doesn't convert elb created_time into dtobj like it does for others
            self.elb.created_time = boto.utils.parse_ts(self.elb.created_time)
        self.delete_form = ELBDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            elb=self.elb,
            elb_name=self.escape_braces(self.elb.name) if self.elb else '',
            elb_created_time=self.dt_isoformat(self.elb.created_time),
            escaped_elb_name=quote(self.elb.name),
            delete_form=self.delete_form,
            in_use=False,
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='elb_view', renderer=TEMPLATE)
    def elb_view(self):
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
        }))


class CreateELBView(BaseView):
    """Create ELB wizard"""
    TEMPLATE = '../templates/elbs/elb_wizard.pt'

    def __init__(self, request):
        super(CreateELBView, self).__init__(request)
        self.ec2_conn = self.get_connection()
        self.iam_conn = self.get_connection(conn_type='iam')
        self.elb_conn = self.get_connection(conn_type='elb')
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.create_form = CreateELBForm(
            self.request, conn=self.ec2_conn, vpc_conn=self.vpc_conn, formdata=self.request.params or None)
        self.certificate_form = CertificateForm(self.request, conn=self.ec2_conn, iam_conn=self.iam_conn, elb_conn=self.elb_conn, formdata=self.request.params or None)
        filter_keys = ['id', 'name', 'placement', 'state', 'tags']
        filters_form = ELBInstancesFiltersForm(
            self.request, ec2_conn=self.ec2_conn, autoscale_conn=self.autoscale_conn,
            iam_conn=None, vpc_conn=self.vpc_conn,
            cloud_type=self.cloud_type, formdata=self.request.params or None)
        search_facets = filters_form.facets
        self.render_dict = dict(
            create_form=self.create_form,
            certificate_form=self.certificate_form,
            security_group_placeholder_text=_(u'Select...'),
            filter_keys=filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='elb_new', renderer=TEMPLATE)
    def elb_view(self):
        return self.render_dict

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'protocol_list': self.get_protocol_list(),
            'port_range_pattern':'^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$',
            'default_vpc_network': self.get_default_vpc_network(),
            'vpc_subnet_choices': self.get_vpc_subnets(),
            'securitygroups_json_endpoint': self.request.route_path('securitygroups_json'),
            'instances_json_endpoint': self.request.route_path('instances_json')
        }))

    def get_protocol_list(self):
        return ({ 'name': 'HTTP', 'port': '80' },
                { 'name': 'HTTPS', 'port': '443' },
                { 'name': 'SSL', 'port': '443' },
                { 'name': 'TCP', 'port': 'tcp' })

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
                    subnets.append(dict(
                        id=vpc_subnet.id,
                        vpc_id=vpc_subnet.vpc_id,
                        availability_zone=vpc_subnet.availability_zone,
                        state=vpc_subnet.state,
                        cidr_block=vpc_subnet.cidr_block,
                    ))
        return subnets

    @view_config(route_name='elb_create', request_method='POST', renderer=TEMPLATE)
    def elb_create(self):
        if self.create_form.validate():
            name = self.request.params.get('name')
            elb_listener = self.request.params.get('elb_listener')
            certificate_arn = self.request.params.get('certificate_arn') or None
            listeners_args = self.get_listeners_args()
            vpc_network = self.request.params.get('vpc_network') or None
            if vpc_network == 'None':
                vpc_network = None
            vpc_subnet = self.request.params.get('vpc_subnet') or None
            if vpc_subnet == 'None':
                vpc_subnet = None
            securitygroup = self.request.params.getall('securitygroup') or None
            zone = self.request.params.getall('zone') or None
            instances = self.request.params.getall('instances') or None
            print name
            print elb_listener
            print certificate_arn 
            print listeners_args
            print vpc_network
            print vpc_subnet
            print securitygroup
            print zone
	    print instances
            with boto_error_handler(self.request, self.request.route_path('elbs')):
                self.log_request(_(u"Creating elastic load balancer {0}").format(name))
                if vpc_subnet is None:
                    params = dict(complex_listeners=listeners_args)  
                    self.elb_conn.create_load_balancer(name, zone, **params)
                else:
                    params = dict(subnets=vpc_subnet,
                              security_groups=securitygroup,
                              complex_listeners=listeners_args)  
                    self.elb_conn.create_load_balancer(name, None, **params)
                self.handle_configure_health_check(name)
                self.elb_conn.register_instances(name, instances)
                prefix = _(u'Successfully created elastic load balancer')
                msg = u'{0} {1}'.format(prefix, name)
                location = self.request.route_path('elbs')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
            return self.render_dict

    def get_listeners_args(self):
        listeners_json = self.request.params.get('elb_listener')
        certificate_arn = self.request.params.get('certificate_arn') or None
        listeners = json.loads(listeners_json) if listeners_json else []
        listeners_args = []

        for listener in listeners:
            from_protocol = listener.get('fromProtocol')
            from_port = listener.get('fromPort')
            to_protocol = listener.get('toProtocol')
            to_port = listener.get('toPort')
            if from_protocol == 'HTTPS' or to_protocol == 'HTTPS':
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
            passes_until_unhealthy = self.request.params.get('passes_until_unhealthy')
            ping_target = u"{0}:{1}".format(ping_protocol, ping_port)
            if ping_protocol == 'HTTP' or ping_protocol == 'HTTPS':
                ping_target = u"{0}{1}".format(ping_target, ping_path)
            print ping_target
            hc = HealthCheck(
                timeout=response_timeout,
                interval=time_between_pings,
                healthy_threshold=passes_until_unhealthy,
                unhealthy_threshold=failures_until_unhealthy,
                target=ping_target 
            )
            self.elb_conn.configure_health_check(name, hc)

    @view_config(route_name='certificate_create', request_method='POST', renderer=TEMPLATE)
    def certificate_create(self):
        if self.certificate_form.validate():
            radio = self.request.params.get('certificate_type_radio')
            certificate_name = self.request.params.get('certificate_name')
            private_key = self.request.params.get('private_key')
            public_key_certificate = self.request.params.get('public_key_certificate')
            certificate_chain = self.request.params.get('certificate_chain')
            certificates = self.request.params.get('certificates')
            print radio
            print certificate_name
            print private_key 
            print public_key_certificate 
            print certificate_chain
            print certificates
            with boto_error_handler(self.request):
                certificate_result = self.iam_conn.upload_server_cert(certificate_name, public_key_certificate, private_key, cert_chain=None, path=None)
                prefix = _(u'Successfully uploaded server certificate')
                msg = u'{0} {1}'.format(prefix, certificate_name)
                print certificate_result
                certificate_arn = certificate_result.upload_server_certificate_result.server_certificate_metadata.arn
                return JSONResponse(status=200, message=msg, id=certificate_arn)
        else:
            form_errors = ', '.join(self.certificate_form.get_errors_list())
            return JSONResponse(status=400, message=form_errors)  # Validation failure = bad request
