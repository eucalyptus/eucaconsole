# -*- coding: utf-8 -*-
# Copyright 2013-2015 Hewlett Packard Enterprise Development LP
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
import itertools
import logging
import re
import simplejson as json
import time

from urllib import quote

import boto.utils

from boto.ec2.elb import HealthCheck
from boto.ec2.elb.attributes import ConnectionSettingAttribute, AccessLogAttribute
from boto.exception import BotoServerError
from boto.s3.acl import ACL, Grant, Policy

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config

from ..constants.cloudwatch import (
    MONITORING_DURATION_CHOICES, GRANULARITY_CHOICES, DURATION_GRANULARITY_CHOICES_MAPPING,
    METRIC_TITLE_MAPPING,
    STATISTIC_CHOICES)
from ..constants.elbs import (
    ELB_MONITORING_CHARTS_LIST, ELB_BACKEND_CERTIFICATE_NAME_PREFIX,
    ELB_PREDEFINED_SECURITY_POLICY_NAME_PREFIX, ELB_CUSTOM_SECURITY_POLICY_NAME_PREFIX,
    AWS_ELB_ACCOUNT_IDS)
from ..forms import ChoicesManager
from ..forms.buckets import CreateBucketForm
from ..forms.elbs import (
    ELBForm, ELBDeleteForm, CreateELBForm, ELBHealthChecksForm, ELBsFiltersForm,
    ELBInstancesForm, ELBInstancesFiltersForm, CertificateForm, BackendCertificateForm, SecurityPolicyForm,
)
from ..i18n import _
from ..models import Notification
from ..views import LandingPageView, BaseView, TaggedItemView, JSONResponse
from ..views.cloudwatchapi import CloudWatchAPIMixin
from . import boto_error_handler


class ELBsView(LandingPageView):
    def __init__(self, request):
        super(ELBsView, self).__init__(request)
        self.request = request
        self.ec2_conn = self.get_connection(conn_type="ec2")
        self.elb_conn = self.get_connection(conn_type="elb")
        self.vpc_conn = self.get_connection(conn_type="vpc")
        self.initial_sort_key = 'name'
        self.prefix = '/elbs'
        self.filter_keys = ['name']
        self.sort_keys = self.get_sort_keys()
        self.json_items_endpoint = self.get_json_endpoint('elbs_json')
        self.delete_form = ELBDeleteForm(self.request, formdata=self.request.params or None)
        self.filters_form = ELBsFiltersForm(
            self.request, cloud_type=self.cloud_type, ec2_conn=self.ec2_conn, vpc_conn=self.vpc_conn,
            is_vpc_supported=self.is_vpc_supported(self.request), formdata=self.request.params or None)
        self.render_dict = dict(
            filter_keys=self.filter_keys,
            search_facets=BaseView.escape_json(json.dumps(self.filters_form.facets)),
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
                prefix = _(u'Successfully deleted load balancer')
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
            dict(key='latency', name=_(u'Avg latency (low to high)')),
            dict(key='-latency', name=_(u'Avg latency (high to low)')),
            dict(key='unhealthy_hosts', name=_(u'Unhealthy hosts (low to high)')),
            dict(key='-unhealthy_hosts', name=_(u'Unhealthy hosts (high to low)')),
            dict(key='healthy_hosts', name=_(u'Healthy hosts (low to high)')),
            dict(key='-healthy_hosts', name=_(u'Healthy hosts (high to low)')),
        ]


class ELBsJsonView(LandingPageView, CloudWatchAPIMixin):
    """JSON response view for ELB landing page"""
    def __init__(self, request, elb_conn=None, cw_conn=None, **kwargs):
        super(ELBsJsonView, self).__init__(request, **kwargs)
        self.elb_conn = elb_conn or self.get_connection(conn_type='elb')
        self.cw_conn = cw_conn or self.get_connection(conn_type='cloudwatch')
        with boto_error_handler(request):
            self.items = self.get_items()

        # Filter items based on MSB params
        if self.is_vpc_supported(self.request):
            subnet = self.request.params.get('subnet')
            if subnet:
                self.items = self.filter_by_vpc_subnet(self.items, subnet=subnet)
        else:
            zone = self.request.params.get('availability_zone')
            if zone:
                self.items = self.filter_by_availability_zone(self.items, zone=zone)

    @view_config(route_name='elbs_json', renderer='json', request_method='POST')
    def elbs_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        with boto_error_handler(self.request):
            elbs_array = []
            for elb in self.items:
                name = elb.name
                health_counts = self.get_elb_health_counts(elb)
                elbs_array.append(dict(
                    dns_name=elb.dns_name,
                    name=name,
                    healthy_hosts=health_counts.get('healthy'),
                    unhealthy_hosts=health_counts.get('unhealthy'),
                    latency=self.get_average_latency(elb),
                ))
            return dict(results=elbs_array)

    def get_items(self):
        return self.elb_conn.get_all_load_balancers() if self.elb_conn else []

    @staticmethod
    def filter_by_availability_zone(items, zone=None):
        return [item for item in items if zone in item.availability_zones]

    @staticmethod
    def filter_by_vpc_subnet(items, subnet=None):
        return [item for item in items if subnet in item.subnets]

    def get_elb_health_counts(self, elb=None):
        healthy_count = 0
        unhealthy_count = 0
        if elb:
            instances = self.elb_conn.describe_instance_health(elb.name)
            for instance in instances:
                if instance.state == 'InService':
                    healthy_count += 1
                elif instance.state == 'OutOfService':
                    unhealthy_count += 1
        return dict(healthy=healthy_count, unhealthy=unhealthy_count)

    def get_average_latency(self, elb=None, duration=21600):
        """Get average latency for a given duration in milliseconds"""
        period = self.modify_granularity(duration)
        stats = self.get_cloudwatch_stats(
            cw_conn=self.cw_conn, period=period, duration=duration, metric='Latency',
            namespace='AWS/ELB', idtype='LoadBalancerName', ids=[elb.name])
        if stats:
            return sum(stat.get('Average') * 1000 for stat in stats) / len(stats)
        return None


class LbTagSet(dict):
    """
    A TagSet is used to collect the tags associated with a particular
    Load Balancer instance.
    TODO: Remove this when we update to Boto 2.38 or later
    """

    def __init__(self, connection=None, **kwargs):
        super(LbTagSet, self).__init__(**kwargs)
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
    """Base view for ELB detail page tabs/views"""

    def __init__(self, request, elb_conn=None, s3_conn=None, **kwargs):
        super(BaseELBView, self).__init__(request, **kwargs)
        self.request = request
        self.ec2_conn = self.get_connection()
        self.iam_conn = self.get_connection(conn_type='iam')
        self.elb_conn = elb_conn or self.get_connection(conn_type='elb')
        self.s3_conn = s3_conn or self.get_connection(conn_type='s3')
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        self.predefined_policy_choices = ChoicesManager(conn=self.elb_conn).predefined_policy_choices(add_blank=False)
        self.can_list_certificates = True
        if self.iam_conn:
            try:
                self.iam_conn.get_all_server_certs()
            except BotoServerError:
                # IAM policy prevents listing certificates
                self.can_list_certificates = False
        else:
            self.can_list_certificates = False

    def get_elb(self):
        if self.elb_conn:
            elb_param = self.request.matchdict.get('id')
            elbs = self.elb_conn.get_all_load_balancers(load_balancer_names=[elb_param])
            return elbs[0] if elbs else None
        return None

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

    def configure_health_checks(self, name):
        ping_protocol = self.request.params.get('ping_protocol')
        ping_port = self.request.params.get('ping_port')
        ping_path = self.request.params.get('ping_path')
        response_timeout = self.request.params.get('response_timeout')
        time_between_pings = self.request.params.get('time_between_pings')
        failures_until_unhealthy = self.request.params.get('failures_until_unhealthy')
        passes_until_healthy = self.request.params.get('passes_until_healthy')
        ping_target = u"{0}:{1}".format(ping_protocol, ping_port)
        if ping_protocol in ['HTTP', 'HTTPS']:
            if not ping_path.startswith('/'):
                ping_path = '/{0}'.format(ping_path)
            ping_target = u"{0}{1}".format(ping_target, ping_path)
        health_check = HealthCheck(
            timeout=response_timeout,
            interval=time_between_pings,
            healthy_threshold=passes_until_healthy,
            unhealthy_threshold=failures_until_unhealthy,
            target=ping_target
        )
        self.elb_conn.configure_health_check(name, health_check)

    def configure_access_logs(self, elb_name=None, elb=None):
        req_params = self.request.params
        params_logging_enabled = req_params.get('logging_enabled') == 'y'
        params_bucket_name = req_params.get('bucket_name')
        params_bucket_prefix = req_params.get('bucket_prefix', '')
        params_collection_interval = int(req_params.get('collection_interval', 60))
        if elb is not None:
            existing_access_log = self.elb_conn.get_lb_attribute(elb.name, 'accessLog')
            unchanged_conditions = [
                existing_access_log.enabled == params_logging_enabled,
                existing_access_log.s3_bucket_name == params_bucket_name,
                existing_access_log.s3_bucket_prefix == params_bucket_prefix,
                existing_access_log.emit_interval == params_collection_interval,
            ]
            if all(unchanged_conditions):
                return None  # Skip if nothing has changed in the ELB's access log config
        # Set Access Logs
        elb_name = elb.name if elb is not None else elb_name
        bucket_prefix = params_bucket_prefix
        if params_logging_enabled:
            self.configure_logging_bucket(bucket_name=params_bucket_name, bucket_prefix=bucket_prefix)
        new_access_log_config = AccessLogAttribute()
        new_access_log_config.enabled = params_logging_enabled
        new_access_log_config.s3_bucket_name = params_bucket_name
        new_access_log_config.s3_bucket_prefix = bucket_prefix
        new_access_log_config.emit_interval = params_collection_interval
        self.elb_conn.modify_lb_attribute(elb_name, 'accessLog', new_access_log_config)

    def configure_logging_bucket(self, bucket_name=None, bucket_prefix=None):
        if bucket_name and bucket_prefix is not None and self.s3_conn:
            existing_bucket_names = [bucket.name for bucket in self.s3_conn.get_all_buckets()]
            if bucket_name in existing_bucket_names:
                bucket = self.s3_conn.lookup(bucket_name, validate=False)
            else:
                self.log_request(u"Creating ELB access logs bucket {0}".format(bucket_name))
                bucket = self.s3_conn.create_bucket(bucket_name)
            # Create access logs folder
            bucket_prefix_exists = bucket.get_key(u'{0}/'.format(bucket_prefix))
            if not bucket_prefix_exists:
                bucket_prefix = bucket_prefix.replace('/', '_')
                bucket_prefix_key = u'{0}/'.format(bucket_prefix)
                self.log_request(u"Creating ELB access logs folder {0} in bucket {1}".format(
                    bucket_prefix_key, bucket_name))
                new_folder = bucket.new_key(bucket_prefix_key)
                new_folder.set_contents_from_string('')
            self.configure_logging_bucket_acl(bucket)

    def configure_logging_bucket_acl(self, bucket=None):
        if self.cloud_type == 'aws':
            # Get AWS ELB account ID based on region
            grant_id = AWS_ELB_ACCOUNT_IDS.get(self.region)
        else:
            admin = self.get_connection(conn_type='admin')
            elb_svc = admin.get_all_services(service_type='loadbalancing')
            # log additional info for unexpected condition
            if len(elb_svc) < 1 and len(elb_svc[0].accounts) < 1:
                logging.error('ERROR: Eucalyptus not returning account info with loadbalancing service!')
            grant_id = elb_svc[0].accounts[0].account_number
        sharing_acl = ACL()
        sharing_acl.add_grant(Grant(
            permission='WRITE',
            type='CanonicalUser',
            id=grant_id,
        ))
        sharing_policy = Policy()
        sharing_policy.acl = sharing_acl
        sharing_policy.owner = bucket.get_acl().owner
        bucket.set_acl(sharing_policy)

    def handle_backend_certificate_create(self, elb_name):
        if self.cloud_type == 'aws':
            return None  # Eucalyptus only
        backend_certificates_json = self.request.params.get('backend_certificates')
        backend_certificates = json.loads(backend_certificates_json) if backend_certificates_json else []
        public_policy_attributes = dict()
        public_policy_type = u'PublicKeyPolicyType'
        backend_policy_type = u'BackendServerAuthenticationPolicyType'
        random_string = self.generate_random_string(length=8)
        backend_policy_name = u'BackendPolicy-{0}-{1}'.format(random_string, elb_name)
        backend_policy_params = {'LoadBalancerName': elb_name,
                                 'PolicyName': backend_policy_name,
                                 'PolicyTypeName': backend_policy_type}
        index = 1
        for cert in backend_certificates:
            public_policy_name = u'{0}-{1}'.format(ELB_BACKEND_CERTIFICATE_NAME_PREFIX, cert.get('name'))
            public_policy_attributes['PublicKey'] = cert.get('certificateBody')
            self.elb_conn.create_lb_policy(elb_name, public_policy_name, public_policy_type, public_policy_attributes)
            backend_policy_params['PolicyAttributes.member.%d.AttributeName' % index] = 'PublicKeyPolicyName'
            backend_policy_params['PolicyAttributes.member.%d.AttributeValue' % index] = public_policy_name
            index += 1
        self.elb_conn.get_status('CreateLoadBalancerPolicy', backend_policy_params)
        # sleep is needed for the previous policy creation to complete
        time.sleep(index)
        instance_port = 443
        self.elb_conn.set_lb_policies_of_backend_server(elb_name, instance_port, backend_policy_name)

    def set_security_policy(self, elb_name, elb=None):
        """
        See http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/ssl-config-update.html
        """
        if self.cloud_type == 'aws':
            return None  # Eucalyptus only
        req_params = self.request.params
        flattened_listeners = [x for x in itertools.chain.from_iterable(self.get_listeners_args())]
        has_https_listener = 443 in flattened_listeners
        if not has_https_listener:
            return None  # Don't set security policy unless an HTTPS listener is set
        elb_security_policy_updated = req_params.get('elb_security_policy_updated') == 'on'
        if not elb_security_policy_updated:
            return None  # Don't set security policy unless Security Policy dialog submit button has been clicked
        latest_predefined_policy = self.get_latest_predefined_policy()
        if not latest_predefined_policy:
            return None  # Policy will fail unless at least one predefined security policy is configured for the cloud
        using_custom_policy = req_params.get('elb_ssl_using_custom_policy') == 'on'
        selected_predefined_policy = req_params.get('elb_predefined_policy')
        random_string = self.generate_random_string(length=8)
        if self.elb_conn:
            policy_type = 'SSLNegotiationPolicyType'
            if using_custom_policy:
                # Create custom security policy
                elb_ssl_protocols = json.loads(req_params.get('elb_ssl_protocols', '[]'))
                elb_ssl_ciphers = json.loads(req_params.get('elb_ssl_ciphers', '[]'))
                using_server_order_pref = req_params.get('elb_ssl_server_order_pref') == 'on'
                policy_name = '{0}-{1}'.format(ELB_CUSTOM_SECURITY_POLICY_NAME_PREFIX, random_string)
                policy_attributes = {'Reference-Security-Policy': latest_predefined_policy}
                for protocol in elb_ssl_protocols:
                    policy_attributes.update({protocol: True})
                for cipher in elb_ssl_ciphers:
                    policy_attributes.update({cipher: True})
                if using_server_order_pref:
                    policy_attributes.update({'Server-Defined-Cipher-Order': True})
                self.elb_conn.create_lb_policy(elb_name, policy_name, policy_type, policy_attributes)
                time.sleep(1)  # Give new policy time to persist before setting ELB security policy for HTTPS listener
            else:
                # Create predefined security policy
                policy_name = '{0}-{1}'.format(selected_predefined_policy, random_string)
                policy_attributes = {'Reference-Security-Policy': selected_predefined_policy}
                self.elb_conn.create_lb_policy(elb_name, policy_name, policy_type, policy_attributes)
                time.sleep(1)  # Give new policy time to persist before setting ELB security policy for HTTPS listener
            # Set security policy for HTTPS listener in ELB
            policies = [policy_name]
            self.elb_conn.set_lb_policies_of_listener(elb_name, 443, policies)

    def get_latest_predefined_policy(self):
        if self.predefined_policy_choices:
            return self.predefined_policy_choices[0][0]

    def get_security_policy(self, elb=None):
        """Get SSL security policy attached to an ELB"""
        if self.cloud_type == 'aws':
            return None  # Eucalyptus only
        if elb:
            if elb.policies:
                for policy in elb.policies.other_policies:
                    if policy.policy_name.startswith(ELB_PREDEFINED_SECURITY_POLICY_NAME_PREFIX):
                        return policy.policy_name
                    elif policy.policy_name.startswith(ELB_CUSTOM_SECURITY_POLICY_NAME_PREFIX):
                        return policy.policy_name
        return self.get_latest_predefined_policy()

    @staticmethod
    def get_health_check_port(elb=None):
        if elb and elb.health_check.target is not None:
            match = re.search('^(\w+):(\d+)/?(.+)?', elb.health_check.target)
            ping_port = match.group(2)
            return ping_port

    @staticmethod
    def get_instance_selector_text():
        instance_selector_text = {'name': _(u'NAME (ID)'), 'tags': _(u'TAGS'),
                                  'zone': _(u'AVAILABILITY ZONE'), 'subnet': _(u'VPC SUBNET'),
                                  'status': _(u'STATUS'), 'status_descr': _(u'STATUS DESCRIPTION'),
                                  'no_matching_instance_error_msg': _(u'No matching instances')}
        return instance_selector_text

    @staticmethod
    def get_instance_health_status_names():
        """Map ELB instance health status to human-friendly names"""
        return {
            'InService': _(u'In service'),
            'OutOfService': _(u'Out of service'),
        }

    def get_protocol_list(self):
        protocol_list = (
            {'name': 'HTTP', 'value': 'HTTP', 'port': '80'},
            {'name': 'HTTPS', 'value': 'HTTPS', 'port': '443'},
            {'name': 'TCP', 'value': 'TCP', 'port': '80'},
            {'name': 'SSL', 'value': 'SSL', 'port': '443'}
        )
        reduced_protocol_list = (
            {'name': 'HTTP', 'value': 'HTTP', 'port': '80'},
            {'name': 'TCP', 'value': 'TCP', 'port': '80'}
        )
        if self.cloud_type == 'euca' and self.can_list_certificates:
            return protocol_list
        else:
            # AWS and Euca w/o IAM perms
            return reduced_protocol_list

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

    def get_vpc_network_name(self, elb=None):
        if elb and self.is_vpc_supported:
            if elb.vpc_id and self.vpc_conn:
                with boto_error_handler(self.request):
                    vpc_networks = self.vpc_conn.get_all_vpcs(vpc_ids=elb.vpc_id)
                    if vpc_networks:
                        vpc_name = TaggedItemView.get_display_name(vpc_networks[0])
                        return vpc_name
        return 'None'


class ELBView(BaseELBView):
    """ELB detail page - General tab"""
    TEMPLATE = '../templates/elbs/elb_view.pt'

    def __init__(self, request, elb_conn=None, elb=None, elb_tags=None, **kwargs):
        super(ELBView, self).__init__(request, elb_conn=elb_conn, **kwargs)
        with boto_error_handler(request):
            self.elb = elb or self.get_elb()
            self.access_logs = self.elb_conn.get_lb_attribute(
                self.elb.name, 'accessLog') if self.elb_conn and self.elb else None
            if self.elb:
                if self.elb.created_time:
                    # boto doesn't convert elb created_time into dtobj like it does for others
                    self.elb.created_time = boto.utils.parse_ts(self.elb.created_time)
                tags_params = {'LoadBalancerNames.member.1': self.elb.name}
                self.elb.tags = elb_tags or self.elb_conn.get_object('DescribeTags', tags_params, LbTagSet)
            else:
                raise HTTPNotFound()
        self.elb_form = ELBForm(
            self.request, conn=self.ec2_conn, vpc_conn=self.vpc_conn,
            elb=self.elb, elb_conn=self.elb_conn, s3_conn=self.s3_conn, securitygroups=self.get_security_groups(),
            formdata=self.request.params or None)
        self.certificate_form = CertificateForm(
            self.request, conn=self.ec2_conn, iam_conn=self.iam_conn, elb_conn=self.elb_conn,
            can_list_certificates=self.can_list_certificates, formdata=self.request.params or None)
        self.backend_certificate_form = BackendCertificateForm(
            self.request, conn=self.ec2_conn, iam_conn=self.iam_conn, elb_conn=self.elb_conn,
            formdata=self.request.params or None)
        self.security_policy_form = SecurityPolicyForm(
            self.request, elb_conn=self.elb_conn, predefined_policy_choices=self.predefined_policy_choices,
            formdata=self.request.params or None
        )
        self.create_bucket_form = CreateBucketForm(self.request, formdata=self.request.params or None)
        self.delete_form = ELBDeleteForm(self.request, formdata=self.request.params or None)
        bucket_name = self.access_logs.s3_bucket_name
        logs_prefix = self.access_logs.s3_bucket_prefix
        logs_subpath = logs_prefix.split('/') if logs_prefix else []
        logs_url = None
        bucket_url = None
        if bucket_name:
            logs_url = self.request.route_path('bucket_contents', name=bucket_name, subpath=logs_subpath)
            bucket_url = self.request.route_path('bucket_contents', name=bucket_name, subpath=[])
        self.render_dict = dict(
            elb=self.elb,
            elb_name=self.escape_braces(self.elb.name) if self.elb else '',
            elb_created_time=self.dt_isoformat(self.elb.created_time) if self.elb and self.elb.created_time else '',
            escaped_elb_name=quote(self.elb.name) if self.elb else '',
            elb_tags=TaggedItemView.get_tags_display(self.elb.tags) if self.elb.tags else '',
            elb_form=self.elb_form,
            security_policy_form=self.security_policy_form,
            latest_predefined_policy=self.get_latest_predefined_policy(),
            elb_security_policy=self.get_security_policy(elb=self.elb),
            delete_form=self.delete_form,
            certificate_form=self.certificate_form,
            backend_certificate_form=self.backend_certificate_form,
            protocol_list=self.get_protocol_list(),
            listener_list=self.get_listener_list(),
            is_vpc_supported=self.is_vpc_supported,
            elb_vpc_network=self.get_vpc_network_name(self.elb),
            security_group_placeholder_text=_(u'Select...'),
            create_bucket_form=self.create_bucket_form,
            controller_options_json=self.get_controller_options_json(),
            logs_url=logs_url,
            bucket_url=bucket_url,
        )

    @view_config(route_name='elb_view', renderer=TEMPLATE)
    def elb_view(self):
        return self.render_dict

    @view_config(route_name='elb_update', request_method='POST', renderer=TEMPLATE)
    def elb_update(self):
        if self.elb_form.validate():
            idle_timeout = self.request.params.get('idle_timeout')
            securitygroup = self.request.params.getall('securitygroup') or None
            listeners_args = self.get_listeners_args()
            location = self.request.route_path('elb_view', id=self.elb.name)
            prefix = _(u'Unable to update load balancer')
            template = u'{0} {1} - {2}'.format(prefix, self.elb.name, '{0}')
            backend_certificates = self.request.params.get('backend_certificates') or None
            with boto_error_handler(self.request, location, template):
                self.update_elb_idle_timeout(self.elb.name, idle_timeout)
                self.update_listeners(listeners_args)
                time.sleep(1)  # Delay is needed to avoid missing listeners post-update
                self.update_elb_tags(self.elb.name)
                self.set_security_policy(self.elb.name)
                self.configure_access_logs(elb=self.elb)
                if self.is_vpc_supported and self.elb.security_groups != securitygroup:
                    self.elb_conn.apply_security_groups_to_lb(self.elb.name, securitygroup)
                if backend_certificates is not None and backend_certificates != '[]':
                    self.handle_backend_certificate_create(self.elb.name)
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

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'is_vpc_supported': self.is_vpc_supported,
            'default_vpc_network': self.get_default_vpc_network(),
            'elb_vpc_network': self.elb.vpc_id if self.elb else [],
            'elb_vpc_subnets': self.elb.subnets if self.elb else [],
            'securitygroups': self.elb.security_groups if self.elb else [],
            'existing_certificate_choices': self.certificate_form.certificate_arn.choices,
            'logging_enabled': self.access_logs.enabled if self.access_logs else False,
            'bucket_choices': dict(self.elb_form.bucket_name.choices),
            'securitygroups_json_endpoint': self.request.route_path('securitygroups_json'),
            'ping_port': self.get_health_check_port(self.elb),
        }))

    def update_elb_idle_timeout(self, elb_name, idle_timeout):
        if self.elb_conn:
            setting_attribute = ConnectionSettingAttribute()
            setting_attribute.idle_timeout = idle_timeout
            self.elb_conn.modify_lb_attribute(elb_name, 'connectingSettings', setting_attribute)

    def get_listener_list(self):
        listener_list = []
        if self.elb and self.elb.listeners:
            for listener in self.elb.listeners:
                listener_dict = {
                    'from_port': listener.load_balancer_port,
                    'to_port': listener.instance_port,
                    'from_protocol': listener.protocol,
                    'to_protocol': listener.instance_protocol
                }
                if listener.ssl_certificate_id:
                    certificate_id = listener.ssl_certificate_id.split('/')[-1]
                    listener_dict.update({
                        'certificate_id': certificate_id,
                        'backend_policies': self.get_backend_policies(),
                    })
                listener_list.append(listener_dict)
        return listener_list

    def get_backend_policies(self):
        backend_certificates = []
        if self.elb and self.cloud_type == 'euca':
            for backend in self.elb.backends:
                backend_certificates.extend(
                    [policy.policy_name for policy in backend.policies if backend.instance_port == 443])
        return backend_certificates

    def update_listeners(self, listeners_args):
        if self.elb_conn and self.elb:
            # Convert strs in existing ELB listeners to unicode objects for add/remove comparisons
            normalized_elb_listeners = []
            if self.elb.listeners:
                for listener in self.elb.listeners:
                    normalized_elb_listeners.append(self.normalize_listener(listener))

            listeners_to_add = [x for x in listeners_args if x not in normalized_elb_listeners]
            listeners_to_remove = [x[0] for x in normalized_elb_listeners if x not in listeners_args]
            self.cleanup_security_policies(delete_stale_policies=True)
            if listeners_to_remove:
                if 443 in listeners_to_remove:
                    self.cleanup_backend_policies()  # Note: this must be before HTTPS listeners are removed
                self.elb_conn.delete_load_balancer_listeners(self.elb.name, listeners_to_remove)
                time.sleep(1)  # sleep is needed for Eucalyptus to avoid not finding the elb error

            if listeners_to_add:
                self.elb_conn.create_load_balancer_listeners(self.elb.name, complex_listeners=listeners_to_add)
                time.sleep(1)  # sleep is needed for Eucalyptus to avoid not finding the elb error

    def cleanup_security_policies(self, delete_stale_policies=False):
        """Empty security policies before setting them in ELB"""
        if self.elb_conn and self.elb and self.cloud_type == 'euca':
            elb_security_policy_updated = self.request.params.get('elb_security_policy_updated') == 'on'
            if not elb_security_policy_updated:
                return None  # Skip cleanup if security policy wasn't updated
            elb_listener_ports = [x[0] for x in self.elb.listeners]
            if 443 in elb_listener_ports:
                self.elb_conn.set_lb_policies_of_listener(self.elb.name, 443, [])
                if delete_stale_policies:
                    self.delete_stale_policies()

    def delete_stale_policies(self):
        if self.elb and self.elb.policies and self.elb.policies.other_policies and self.cloud_type == 'euca':
            for policy in self.elb.policies.other_policies:
                policy_name_conditions = [
                    policy.policy_name.startswith(ELB_PREDEFINED_SECURITY_POLICY_NAME_PREFIX),
                    policy.policy_name.startswith(ELB_CUSTOM_SECURITY_POLICY_NAME_PREFIX),
                ]
                if any(policy_name_conditions):
                    self.elb_conn.delete_lb_policy(self.elb.name, policy.policy_name)

    def cleanup_backend_policies(self):
        if self.elb_conn and self.elb and self.cloud_type == 'euca':
            elb_listener_ports = [x[0] for x in self.elb.listeners]
            if self.elb.backends and 443 in elb_listener_ports:
                self.elb_conn.set_lb_policies_of_backend_server(self.elb.name, 443, [])

    @staticmethod
    def normalize_listener(listener):
        """Listeners obtained from API call aren't exactly the same format as the listener_args,
           so normalize them (i.e. convert strings to unicode and set tuple to 4 items) for comparison checks"""
        normalized_listener = []
        if type(listener) != tuple:
            listener = listener.get_tuple()
        for item in listener:
            if item:
                if type(item) == int:
                    normalized_listener.append(item)
                else:
                    normalized_listener.append(unicode(item))
        if len(normalized_listener) < 4:
            normalized_listener.append(normalized_listener[2])
        return tuple(normalized_listener)

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

    def get_security_groups(self):
        securitygroups = []
        if self.elb and self.elb.vpc_id:
            with boto_error_handler(self.request):
                securitygroups = self.ec2_conn.get_all_security_groups(filters={'vpc-id': [self.elb.vpc_id]})
        return securitygroups


class ELBInstancesView(BaseELBView):
    """ELB detail page - Instances tab"""
    TEMPLATE = '../templates/elbs/elb_instances.pt'

    def __init__(self, request, elb=None, elb_attrs=None, **kwargs):
        super(ELBInstancesView, self).__init__(request, **kwargs)
        with boto_error_handler(request):
            self.elb = elb or self.get_elb()
            if not self.elb:
                raise HTTPNotFound()
            self.cross_zone_enabled = self.is_cross_zone_enabled(elb_attrs=elb_attrs)
        self.elb_form = ELBInstancesForm(
            self.request, elb=self.elb, cross_zone_enabled=self.cross_zone_enabled,
            formdata=self.request.params or None)
        filters_form = ELBInstancesFiltersForm(
            self.request, ec2_conn=self.ec2_conn, autoscale_conn=self.autoscale_conn,
            iam_conn=None, vpc_conn=self.vpc_conn,
            cloud_type=self.cloud_type, formdata=self.request.params or None)
        search_facets = filters_form.facets
        filter_keys = ['id', 'name', 'placement', 'state', 'tags', 'vpc_subnet_display', 'vpc_name']
        self.render_dict = dict(
            elb=self.elb,
            elb_name=self.escape_braces(self.elb.name) if self.elb else '',
            escaped_elb_name=quote(self.elb.name) if self.elb else '',
            elb_vpc_network=self.get_vpc_network_name(self.elb),
            elb_form=self.elb_form,
            delete_form=ELBDeleteForm(self.request, formdata=self.request.params or None),
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            filter_keys=filter_keys,
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='elb_instances', renderer=TEMPLATE)
    def elb_instances(self):
        return self.render_dict

    @view_config(route_name='elb_instances_update', request_method='POST', renderer=TEMPLATE)
    def elb_instances_update(self):
        if self.elb_form.validate():
            vpc_subnet = self.request.params.getall('vpc_subnet') or None
            if vpc_subnet == 'None':
                vpc_subnet = None
            zone = self.request.params.getall('zone') or None
            cross_zone_enabled = self.request.params.get('cross_zone_enabled') == 'y'
            instances = self.request.params.getall('instances') or None
            location = self.request.route_path('elb_instances', id=self.elb.name)
            prefix = _(u'Unable to update load balancer')
            template = u'{0} {1} - {2}'.format(prefix, self.elb.name, '{0}')
            with boto_error_handler(self.request, location, template):
                if vpc_subnet is None:
                    self.update_elb_zones(self.elb.name, self.elb.availability_zones, zone)
                    if cross_zone_enabled:
                        self.elb_conn.modify_lb_attribute(self.elb.name, 'crossZoneLoadBalancing', True)
                    else:
                        self.elb_conn.modify_lb_attribute(self.elb.name, 'crossZoneLoadBalancing', False)
                else:
                    self.update_elb_subnets(self.elb.name, self.elb.subnets, vpc_subnet)
                self.update_elb_instances(self.elb.name, self.elb.instances, instances)
                prefix = _(u'Successfully updated load balancer')
                msg = u'{0} {1}'.format(prefix, self.elb.name)
                self.log_request(u"{0} {1}".format(msg, self.elb.name))
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.elb_form.get_errors_list()
        return self.render_dict

    def is_cross_zone_enabled(self, elb_attrs=None):
        attrs = elb_attrs or self.elb.get_attributes()
        return attrs.cross_zone_load_balancing.enabled

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'is_vpc_supported': self.is_vpc_supported,
            'default_vpc_network': self.get_default_vpc_network(),
            'availability_zones': self.elb.availability_zones if self.elb else [],
            'availability_zone_choices': self.get_availability_zones(),
            'vpc_subnet_choices': self.get_vpc_subnets(),
            'elb_vpc_network': self.elb.vpc_id if self.elb else [],
            'elb_vpc_subnets': self.elb.subnets if self.elb else [],
            'instance_selector_text': self.get_instance_selector_text(),
            'health_status_names': self.get_instance_health_status_names(),
            'all_instances': self.get_all_instances(),
            'elb_instance_health': self.get_elb_instance_health(),
            'instances': self.get_elb_instance_list(),
            'instances_json_endpoint': self.request.route_path('instances_json'),
            'cross_zone_enabled': self.cross_zone_enabled,
        }))

    def get_all_instances(self):
        instances = []
        if self.ec2_conn:
            with boto_error_handler(self.request):
                reservations = self.ec2_conn.get_all_reservations()
            for reservation in reservations:
                for instance in reservation.instances:
                    instances.append(dict(
                        id=instance.id,
                        vpc_id=instance.vpc_id,
                        subnet_id=instance.subnet_id,
                        zone=instance.placement,
                    ))
        return instances

    def get_elb_instance_health(self):
        instance_health = []
        if self.elb_conn and self.elb:
            instances = self.elb_conn.describe_instance_health(self.elb.name)
            for instance in instances:
                instance_health.append(dict(
                    instance_id=instance.instance_id,
                    state=instance.state,
                    description=instance.description,
                ))
        return instance_health

    def get_elb_instance_list(self):
        instances = []
        if self.elb and self.elb.instances:
            for instance in self.elb.instances:
                if instance:
                    instances.append(instance.id)
        return instances

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
            time.sleep(1)  # Delay needed to prevent missing instances on subsequent page load
        if add_instances:
            self.elb_conn.register_instances(elb_name, add_instances)
            time.sleep(1)  # Delay needed to prevent missing instances on subsequent page load


class ELBHealthChecksView(BaseELBView):
    """ELB detail page - Health Checks tab"""
    TEMPLATE = '../templates/elbs/elb_healthchecks.pt'

    def __init__(self, request, elb=None, **kwargs):
        super(ELBHealthChecksView, self).__init__(request, **kwargs)
        with boto_error_handler(request):
            self.elb = elb or self.get_elb()
            if not self.elb:
                raise HTTPNotFound()
            self.elb_form = ELBHealthChecksForm(
                self.request, s3_conn=self.s3_conn, elb_conn=self.elb_conn, elb=self.elb,
                formdata=self.request.params or None)
        self.render_dict = dict(
            elb=self.elb,
            elb_name=self.escape_braces(self.elb.name) if self.elb else '',
            elb_form=self.elb_form,
            escaped_elb_name=quote(self.elb.name) if self.elb else '',
            delete_form=ELBDeleteForm(self.request, formdata=self.request.params or None),
        )

    @view_config(route_name='elb_healthchecks', renderer=TEMPLATE)
    def elb_healthchecks(self):
        return self.render_dict

    @view_config(route_name='elb_healthchecks_update', request_method='POST', renderer=TEMPLATE)
    def elb_healthchecks_update(self):
        if self.elb_form.validate():
            location = self.request.route_path('elb_healthchecks', id=self.elb.name)
            prefix = _(u'Unable to update load balancer')
            template = u'{0} {1} - {2}'.format(prefix, self.elb.name, '{0}')
            with boto_error_handler(self.request, location, template):
                self.configure_health_checks(self.elb.name)
                prefix = _(u'Successfully updated health checks for')
                msg = u'{0} {1}'.format(prefix, self.elb.name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.elb_form.get_errors_list()
        return self.render_dict


class ELBMonitoringView(BaseELBView):
    """ELB detail page - Monitoring tab"""
    TEMPLATE = '../templates/elbs/elb_monitoring.pt'

    def __init__(self, request, elb=None, **kwargs):
        super(ELBMonitoringView, self).__init__(request, **kwargs)
        with boto_error_handler(request):
            self.elb = elb or self.get_elb()
            if not self.elb:
                raise HTTPNotFound()
            self.availability_zones = [zone.get('id') for zone in self.get_availability_zones()]
        self.render_dict = dict(
            elb=self.elb,
            elb_name=self.escape_braces(self.elb.name) if self.elb else '',
            escaped_elb_name=quote(self.elb.name) if self.elb else '',
            duration_choices=MONITORING_DURATION_CHOICES,
            statistic_choices=STATISTIC_CHOICES,
            controller_options_json=self.get_controller_options_json()
        )

    @view_config(route_name='elb_monitoring', renderer=TEMPLATE)
    def elb_monitoring(self):
        return self.render_dict

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'metric_title_mapping': METRIC_TITLE_MAPPING,
            'charts_list': ELB_MONITORING_CHARTS_LIST,
            'granularity_choices': GRANULARITY_CHOICES,
            'duration_granularities_mapping': DURATION_GRANULARITY_CHOICES_MAPPING,
            'availability_zones': self.availability_zones,
        }))


class CreateELBView(BaseELBView):
    """Create ELB wizard"""
    TEMPLATE = '../templates/elbs/elb_wizard.pt'

    def __init__(self, request):
        super(CreateELBView, self).__init__(request)
        # Note: CreateELBForm contains (inherits from) ELBHealthChecksForm
        self.create_form = CreateELBForm(
            self.request, conn=self.ec2_conn, vpc_conn=self.vpc_conn, s3_conn=self.s3_conn,
            formdata=self.request.params or None)
        self.create_bucket_form = CreateBucketForm(self.request, formdata=self.request.params or None)
        self.certificate_form = CertificateForm(
            self.request, conn=self.ec2_conn, iam_conn=self.iam_conn, elb_conn=self.elb_conn,
            can_list_certificates=self.can_list_certificates, formdata=self.request.params or None)
        self.backend_certificate_form = BackendCertificateForm(
            self.request, conn=self.ec2_conn, iam_conn=self.iam_conn, elb_conn=self.elb_conn,
            formdata=self.request.params or None)
        self.security_policy_form = SecurityPolicyForm(
            self.request, elb_conn=self.elb_conn, predefined_policy_choices=self.predefined_policy_choices,
            formdata=self.request.params or None
        )
        filter_keys = ['id', 'name', 'placement', 'state', 'security_groups', 'vpc_subnet_display', 'vpc_name']
        filters_form = ELBInstancesFiltersForm(
            self.request, ec2_conn=self.ec2_conn, autoscale_conn=self.autoscale_conn,
            iam_conn=None, vpc_conn=self.vpc_conn,
            cloud_type=self.cloud_type, formdata=self.request.params or None)
        search_facets = filters_form.facets
        self.render_dict = dict(
            create_form=self.create_form,
            create_bucket_form=self.create_bucket_form,
            certificate_form=self.certificate_form,
            backend_certificate_form=self.backend_certificate_form,
            can_list_certificates=self.can_list_certificates,
            security_policy_form=self.security_policy_form,
            latest_predefined_policy=self.get_latest_predefined_policy(),
            elb_security_policy=self.get_security_policy(),
            protocol_list=self.get_protocol_list(),
            listener_list=[{'from_port': 80, 'to_port': 80, 'from_protocol': 'HTTP', 'to_protocol': 'HTTP'}],  # Set HTTP listener by default
            security_group_placeholder_text=_(u'Select...'),
            is_vpc_supported=self.is_vpc_supported,
            avail_zones_placeholder_text=_(u'Select availability zones'),
            vpc_subnets_placeholder_text=_(u'Select VPC subnets'),
            filter_keys=filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='elb_new', renderer=TEMPLATE)
    def elb_new(self):
        return self.render_dict

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'resource_name': 'elb',
            'wizard_tab_list': self.get_wizard_tab_list(),
            'is_vpc_supported': self.is_vpc_supported,
            'can_list_certificates': self.can_list_certificates,
            'default_vpc_network': self.get_default_vpc_network(),
            'availability_zone_choices': self.get_availability_zones(),
            'vpc_subnet_choices': self.get_vpc_subnets(),
            'instance_selector_text': self.get_instance_selector_text(),
            'securitygroups_json_endpoint': self.request.route_path('securitygroups_json'),
            'instances_json_endpoint': self.request.route_path('instances_json'),
            'existing_certificate_choices': self.certificate_form.certificate_arn.choices,
            'bucket_choices': dict(self.create_form.bucket_name.choices),
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
                self.configure_health_checks(name)
                if instances is not None:
                    self.elb_conn.register_instances(name, instances)
                if cross_zone_enabled == 'y':
                    self.elb_conn.modify_lb_attribute(name, 'crossZoneLoadBalancing', True)
                if backend_certificates is not None and backend_certificates != '[]':
                    self.handle_backend_certificate_create(name)
                self.add_elb_tags(name)
                self.set_security_policy(name)
                if self.request.params.get('logging_enabled') == 'y':
                    self.configure_access_logs(elb_name=name)
                prefix = _(u'Successfully created elastic load balancer')
                msg = u'{0} {1}'.format(prefix, name)
                location = self.request.route_path('elbs')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
            return self.render_dict

    @view_config(route_name='certificate_create', request_method='POST', renderer='json')
    def certificate_create(self):
        if self.certificate_form.validate():
            certificate_name = self.request.params.get('certificate_name')
            private_key = self.request.params.get('private_key')
            public_key_certificate = self.request.params.get('public_key_certificate')
            certificate_chain = self.request.params.get('certificate_chain') or None
            try:
                certificate_result = self.iam_conn.upload_server_cert(
                    certificate_name, public_key_certificate, private_key, cert_chain=certificate_chain)
                prefix = _(u'Successfully uploaded server certificate')
                msg = u'{0} {1}'.format(prefix, certificate_name)
                certificate_arn = certificate_result.upload_server_certificate_result.server_certificate_metadata.arn
                return JSONResponse(status=200, message=msg, id=certificate_arn)
            except BotoServerError as err:
                return JSONResponse(status=400, message=err.message)  # Malformed certificate
        else:
            form_errors = ', '.join(self.certificate_form.get_errors_list())
            return JSONResponse(status=400, message=form_errors)  # Validation failure = bad request
