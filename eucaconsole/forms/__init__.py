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
Base Forms

IMPORTANT: All forms needing CSRF protection should inherit from BaseSecureForm

"""
import logging
import pylibmc
import sys

from wtforms import StringField
from wtforms.ext.csrf import SecureForm
from wtforms.widgets import html_params, HTMLString, Select
from markupsafe import escape

import boto
from boto.exception import BotoServerError

from ..caches import extra_long_term
from ..constants.instances import AWS_INSTANCE_TYPE_CHOICES
from ..i18n import _


BLANK_CHOICE = ('', _(u'Select...'))


class NgNonBindableOptionSelect(Select):
    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        options = {'value': value}
        if selected:
            options['selected'] = u'selected'
        return HTMLString(u'<option %s ng-non-bindable="">%s</option>' % (
            html_params(**options), escape(unicode(label))))


class BaseSecureForm(SecureForm):
    def __init__(self, request, **kwargs):
        self.request = request
        super(BaseSecureForm, self).__init__(**kwargs)

    def generate_csrf_token(self, csrf_context):
        return self.request.session.get_csrf_token() if hasattr(self.request, 'session') else ''

    def get_errors_list(self):
        """Convenience method to get all form validation errors as a list of message strings"""
        from ..views import BaseView
        error_messages = []
        for field, errors in self.errors.items():
            field_errors = BaseView.escape_braces(', '.join(errors))
            msg = '{0}: {1}'.format(field, field_errors)
            error_messages.append(msg)
        return error_messages


class TextEscapedField(StringField):
    def _value(self):
        from ..views import BaseView
        text_type = str if sys.version_info[0] >= 3 else unicode
        return BaseView.escape_braces(text_type(self.data)) if self.data is not None else ''


class GenerateFileForm(BaseSecureForm):
    pass


class ChoicesManager(object):
    """Container for form choices reused across the app"""

    def __init__(self, conn=None):
        """"Note: conn param could be a connection object of any type, based on the choices required"""
        from ..views import BaseView
        self.BaseView = BaseView
        self.conn = conn

    # EC2 connection type choices

    def availability_zones(self, region, zones=None, add_blank=True):
        """Returns a list of availability zone choices. Will fetch zones if not passed"""
        choices = []
        zones = zones or []
        if add_blank:
            choices.append(BLANK_CHOICE)
        if not zones:
            zones.extend(self.get_availability_zones(region))
        for zone in zones:
            choices.append((zone.name, zone.name))
        return sorted(choices)

    def get_availability_zones(self, region):
        @extra_long_term.cache_on_arguments(namespace='availability_zones')
        def _get_zones_cache_(self, region):
            return _get_zones_(self, region)

        def _get_zones_(self, region):
            zones = []
            if self.conn is not None:
                zones = self.conn.get_all_zones()
            return zones
        try:
            return _get_zones_cache_(self, region)
        except pylibmc.Error as err:
            return _get_zones_(self, region)

    def instances(self, instances=None, state=None, escapebraces=True):
        from ..views import TaggedItemView
        choices = [('', _(u'Select instance...'))]
        instances = instances or []
        if not instances and self.conn is not None:
            instances = self.conn.get_only_instances()
            if self.conn:
                for instance in instances:
                    value = instance.id
                    label = TaggedItemView.get_display_name(instance, escapebraces=escapebraces)
                    if state is None or instance.state == state:
                        choices.append((value, label))
        return choices

    def instance_types(self, cloud_type='euca', add_blank=True, add_description=True):
        """Get instance type (e.g. m1.small) choices
            cloud_type is either 'euca' or 'aws'
        """
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        if cloud_type == 'euca':
            types = []

            @extra_long_term.cache_on_arguments(namespace='instance_types')
            def _get_instance_types_cache_(self):
                return _get_instance_types_(self)

            def _get_instance_types_(self):
                types = []
                if self.conn is not None:
                    types = self.conn.get_all_instance_types()
                return types
            try:
                types.extend(_get_instance_types_cache_(self))
            except pylibmc.Error as err:
                types.extend(_get_instance_types_(self))
            choices = []
            for vmtype in types:
                vmtype_str = _(u'{0}: {1} CPUs, {2} memory (MB), {3} disk (GB,root device)').format(
                    self.BaseView.escape_braces(vmtype.name), vmtype.cores, vmtype.memory, vmtype.disk)
                vmtype_tuple = vmtype.name, vmtype_str if add_description else vmtype.name
                choices.append(vmtype_tuple)
            return choices
        elif cloud_type == 'aws':
            if add_description:
                return AWS_INSTANCE_TYPE_CHOICES
            else:
                return [(name, name) for name, description in AWS_INSTANCE_TYPE_CHOICES]

    def volumes(self, volumes=None, escapebraces=True):
        from ..views import TaggedItemView
        choices = [('', _(u'Select volume...'))]
        volumes = volumes or []
        if not volumes and self.conn is not None:
            volumes = self.conn.get_all_volumes()
            if self.conn:
                for volume in volumes:
                    value = volume.id
                    label = TaggedItemView.get_display_name(volume, escapebraces=escapebraces)
                    choices.append((value, label))
        return choices

    def snapshots(self, snapshots=None, escapebraces=True):
        from ..views import TaggedItemView
        choices = [('', _(u'None'))]
        snapshots = snapshots or []
        if not snapshots and self.conn is not None:
            snapshots = self.conn.get_all_snapshots()
            if self.conn:
                for volume in snapshots:
                    value = volume.id
                    label = TaggedItemView.get_display_name(volume, escapebraces=escapebraces)
                    choices.append((value, label))
        return choices

    def security_groups(self, securitygroups=None, use_id=False, add_blank=True, escapebraces=True):
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        security_groups = securitygroups or []
        if not security_groups and self.conn is not None:
            security_groups = self.conn.get_all_security_groups()
        for sgroup in security_groups:
            sg_name = sgroup.name
            if escapebraces:
                sg_name = self.BaseView.escape_braces(sg_name)
            if use_id:
                choices.append((sgroup.id, sg_name))
            else:
                choices.append((sg_name, sg_name))
        if not security_groups:
            choices.append(('default', 'default'))
        return sorted(set(choices))

    def keypairs(self, keypairs=None, add_blank=True, no_keypair_option=False, escapebraces=True):
        choices = []
        keypairs = keypairs or []
        if not keypairs and self.conn is not None:
            keypairs = self.conn.get_all_key_pairs()
        for keypair in keypairs:
            kp_name = keypair.name
            if escapebraces:
                kp_name = self.BaseView.escape_braces(kp_name)
            choices.append((kp_name, kp_name))
        choices = sorted(set(choices))
        # sort actual key pairs prior to prepending blank and appending 'none'
        ret = []
        if add_blank:
            ret.append(BLANK_CHOICE)
        ret.extend(choices)
        if no_keypair_option:
            ret.append(('none', _(u'None (advanced option)')))
        return ret

    def elastic_ips(self, instance=None, ipaddresses=None, add_blank=True):
        choices = []  # ('', _(u'None assigned'))]
        ipaddresses = ipaddresses or []
        if not ipaddresses and self.conn is not None:
            ipaddresses = self.conn.get_all_addresses()
        if instance and instance.state == 'running':
            choices.append(('', _(u'Unassign Address')))
        for eip in ipaddresses:
            if eip.instance_id is None or eip.instance_id == '':
                choices.append((eip.public_ip, eip.public_ip))
        if instance and instance.ip_address:
            choices.append((instance.ip_address, instance.ip_address))
        if instance and instance.ip_address is None and instance.state == 'stopped':
            choices.append(('none', _(u'no address in stopped state')))
        return sorted(set(choices))

    def kernels(self, kernel_images=None, image=None):
        """Get kernel id choices"""
        choices = [('', _(u'Use default from image'))]
        kernel_images = kernel_images or []
        if not kernel_images and self.conn is not None:
            kernel_images = self.conn.get_all_kernels()  # TODO: cache me
        for kernel_image in kernel_images:
            if kernel_image.id:
                choices.append((kernel_image.id, kernel_image.id))
        if image and image.kernel_id is not None:
            choices.append((image.kernel_id, image.kernel_id))
        return sorted(set(choices))

    def ramdisks(self, ramdisk_images=None, image=None):
        """Get ramdisk id choices"""
        choices = [('', _(u'Use default from image'))]
        ramdisk_images = ramdisk_images or []
        if not ramdisk_images and self.conn is not None:
            ramdisk_images = self.conn.get_all_ramdisks()  # TODO: cache me
        for ramdisk_image in ramdisk_images:
            if ramdisk_image.id:
                choices.append((ramdisk_image.id, ramdisk_image.id))
        if image and image.ramdisk_id is not None:
            choices.append((image.ramdisk_id, image.ramdisk_id))
        return sorted(set(choices))

    # AutoScale connection type choices

    def scaling_groups(self, scaling_groups=None, add_blank=True, escapebraces=True):
        """Returns a list of scaling group choices"""
        choices = []
        scaling_groups = scaling_groups or []
        if add_blank:
            choices.append(BLANK_CHOICE)
        # Note: self.conn is an ELBConnection
        if not scaling_groups and self.conn is not None:
            scaling_groups = self.conn.get_all_groups()
        for scaling_group in scaling_groups:
            sg_name = scaling_group.name
            if escapebraces:
                sg_name = self.BaseView.escape_braces(sg_name)
            choices.append((sg_name, sg_name))
        return sorted(choices)

    def launch_configs(self, launch_configs=None, add_blank=True, escapebraces=True):
        """Returns a list of lauch configuration choices"""
        choices = []
        launch_configs = launch_configs or []
        if add_blank:
            choices.append(BLANK_CHOICE)
        # Note: self.conn is an ELBConnection
        if not launch_configs and self.conn is not None:
            launch_configs = self.conn.get_all_launch_configurations()
        for launch_config in launch_configs:
            lc_name = launch_config.name
            if escapebraces:
                lc_name = self.BaseView.escape_braces(lc_name)
            choices.append((lc_name, lc_name))
        return sorted(choices)

    # ELB connection type choices

    def load_balancers(self, load_balancers=None, add_blank=True, escapebraces=True):
        """Returns a list of load balancer choices.  Will fetch load balancers if not passed"""
        choices = []
        try:
            load_balancers = load_balancers or []
            if add_blank:
                choices.append(BLANK_CHOICE)
            # Note: self.conn is an ELBConnection
            if not load_balancers and self.conn is not None:
                load_balancers = self.get_all_load_balancers()
            for load_balancer in load_balancers:
                lb_name = load_balancer.name
                if escapebraces:
                    lb_name = self.BaseView.escape_braces(lb_name)
                choices.append((lb_name, lb_name))
        except BotoServerError as ex:
            if ex.reason == "ServiceUnavailable":
                logging.info("ELB service not available, disabling polling")
            else:
                raise ex
        return sorted(choices)

    # Special version of this to handle case where back end doesn't have ELB configured

    def get_all_load_balancers(self, load_balancer_names=None):
        params = {}
        if load_balancer_names:
            self.conn.build_list_params(params, load_balancer_names, 'LoadBalancerNames.member.%d')
        http_request = self.conn.build_base_http_request(
            'GET', '/', None, params, {}, '', self.conn.server_name())
        http_request.params['Action'] = 'DescribeLoadBalancers'
        http_request.params['Version'] = self.conn.APIVersion
        response = self.conn._mexe(http_request, override_num_retries=2)
        body = response.read()
        boto.log.debug(body)
        if not body:
            boto.log.error('Null body %s' % body)
            raise self.conn.ResponseError(response.status, response.reason, body)
        elif response.status == 200:
            obj = boto.resultset.ResultSet([('member', boto.ec2.elb.loadbalancer.LoadBalancer)])
            h = boto.handler.XmlHandler(obj, self.conn)
            import xml.sax
            xml.sax.parseString(body, h)
            return obj
        else:
            boto.log.error('%s %s' % (response.status, response.reason))
            boto.log.error('%s' % body)
            raise self.conn.ResponseError(response.status, response.reason, body)

    # IAM options

    def roles(self, roles=None, add_blank=True, escapebraces=True):
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        role_list = roles or []
        if not role_list and self.conn is not None:
            role_list = self.conn.list_roles().roles
        for role in role_list:
            rname = role.role_name
            if escapebraces:
                rname = self.BaseView.escape_braces(rname)
            choices.append((rname, rname))
        return sorted(set(choices))

    def accounts(self, add_blank=True, escapebraces=True):
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        account_list = []
        if self.conn is not None:
            account_list = self.conn.get_response('ListAccounts', params={}, list_marker='Accounts').accounts
        for account in account_list:
            rname = account.account_name
            if escapebraces:
                rname = self.BaseView.escape_braces(rname)
            choices.append((rname, rname))
        return sorted(set(choices))

    # S3 connection type choices

    def buckets(self, buckets=None, add_blank=True, escapebraces=True):
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        bucket_list = buckets or []
        if not bucket_list and self.conn is not None:
            bucket_list = self.conn.get_all_buckets()
        for bucket in bucket_list:
            bname = bucket.name
            if escapebraces:
                bname = self.BaseView.escape_braces(bname)
            choices.append((bname, bname))
        return sorted(set(choices))

    # VPC connection type choices

    def vpc_networks(self, vpc_networks=None, add_blank=True,  escapebraces=True):
        from ..views import TaggedItemView
        choices = []
        if add_blank:
            choices = [('', _(u'No VPC'))]
        vpc_network_list = vpc_networks or []
        if not vpc_network_list and self.conn is not None:
            vpc_network_list = self.conn.get_all_vpcs()
        for vpc in vpc_network_list:
            vpc_name = TaggedItemView.get_display_name(vpc, escapebraces=escapebraces)
            choices.append((vpc.id, vpc_name))
        return sorted(set(choices))

    def vpc_subnets(self, vpc_subnets=None, vpc_id=None, show_zone=False, add_blank=True, escapebraces=True):
        choices = []
        if add_blank:
            choices.append(('None', _(u'No subnets found')))
        vpc_subnet_list = vpc_subnets or []
        if not vpc_subnet_list and self.conn is not None:
            if vpc_id:
                vpc_subnet_list = self.conn.get_all_subnets(filters={'vpcId': [vpc_id]})
            else:
                vpc_subnet_list = self.conn.get_all_subnets()
        for vpc in vpc_subnet_list:
            if show_zone:
                # Format the VPC subnet display string for select options
                subnet_string = '{0} ({1}) | {2}'.format(vpc.cidr_block, vpc.id, vpc.availability_zone)
                choices.append((vpc.id, subnet_string))
            else:
                choices.append((vpc.id, vpc.cidr_block))
        return sorted(set(choices))
