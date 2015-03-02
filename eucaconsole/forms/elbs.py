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
Forms for Elastic Load Balancer 

"""
import wtforms
from wtforms import validators

from ..i18n import _
from . import BaseSecureForm, ChoicesManager, TextEscapedField


class ELBDeleteForm(BaseSecureForm):
    """ELB deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


class ELBsFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    availability_zones = wtforms.SelectMultipleField(label=_(u'Availability zone'))
    instance_type = wtforms.SelectMultipleField(label=_(u'Instance type'))
    key_name = wtforms.SelectMultipleField(label=_(u'Key pair'))
    security_groups = wtforms.SelectMultipleField(label=_(u'Security group'))

    def __init__(self, request, cloud_type='euca', ec2_conn=None, **kwargs):
        super(ELBsFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.cloud_type = cloud_type
        self.ec2_conn = ec2_conn
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        region = request.session.get('region')
        self.availability_zones.choices = self.ec2_choices_manager.availability_zones(region, add_blank=False)
        self.instance_type.choices = self.ec2_choices_manager.instance_types(
            add_blank=False, cloud_type=self.cloud_type, add_description=False)
        self.key_name.choices = self.ec2_choices_manager.keypairs(add_blank=False, no_keypair_filter_option=True)
        self.security_groups.choices = self.ec2_choices_manager.security_groups(use_id=True, add_blank=False)
        self.facets = [
            {'name':'instance_type', 'label':self.instance_type.label.text,
                'options':self.getOptionsFromChoices(self.instance_type.choices)},
            {'name':'key_name', 'label':self.key_name.label.text,
                'options':self.getOptionsFromChoices(self.key_name.choices)},
            {'name':'security_group', 'label':self.security_groups.label.text,
                'options':self.getOptionsFromChoices(self.security_groups.choices)},
        ]


class CreateELBForm(BaseSecureForm):
    """Create Elastic Load Balancer form"""
    name_error_msg = _(u'Name must be between 1 and 255 characters long, and must not contain space')
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.InputRequired(message=name_error_msg)],
    )
    vpc_network = wtforms.SelectField(label=_(u'VPC network'))
    vpc_network_helptext = _(u'Launch your instance into one of your Virtual Private Clouds')
    vpc_subnet = wtforms.SelectField(label=_(u'VPC subnets'))
    securitygroup = wtforms.SelectMultipleField(label=_(u'Security groups'))
    zone = wtforms.SelectMultipleField(label=_(u'Availability zones'))
    ping_protocol = wtforms.SelectField(label=_(u'Protocol'))
    ping_port_error_msg = _(u'Port range value must be whole numbers between 1-65535')
    ping_port = wtforms.IntegerField(
        label=_(u'Port'),
        validators=[
            validators.InputRequired(message=ping_port_error_msg),
            validators.NumberRange(min=1, max=65535),
        ],
    )
    ping_path_error_msg = ''
    ping_path = TextEscapedField(
        id=u'ping-path',
        label=_(u'Path'),
        default="/index.html",
    )
    response_timeout_error_msg = _(u'Response timeout is required')
    response_timeout = wtforms.IntegerField(
        label=_(u'Response timeout (secs)'),
        validators=[
            validators.InputRequired(message=response_timeout_error_msg),
        ],
    )
    time_between_pings = wtforms.SelectField(label=_(u'Time between pings'))
    failures_until_unhealthy = wtforms.SelectField(label=_(u'Failures until unhealthy'))
    passes_until_unhealthy = wtforms.SelectField(label=_(u'Passes until unhealthy'))

    def __init__(self, request, conn=None, vpc_conn=None, **kwargs):
        super(CreateELBForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.vpc_conn = vpc_conn
        self.cloud_type = request.session.get('cloud_type', 'euca')
        from ..views import BaseView
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        self.set_error_messages()
        self.choices_manager = ChoicesManager(conn=conn)
        self.vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.set_help_text()
        self.set_choices(request)

    def set_help_text(self):
        self.vpc_network.label_help_text = self.vpc_network_helptext

    def set_choices(self, request):
        if self.cloud_type == 'euca' and self.is_vpc_supported:
            self.vpc_network.choices = self.vpc_choices_manager.vpc_networks(add_blank=False)
        else:
            self.vpc_network.choices = self.vpc_choices_manager.vpc_networks()
        self.vpc_subnet.choices = self.vpc_choices_manager.vpc_subnets()
        self.securitygroup.choices = self.choices_manager.security_groups(
            securitygroups=None, use_id=True, add_blank=False)
        region = request.session.get('region')
        self.zone.choices = self.get_availability_zone_choices(region)
        self.ping_protocol.choices = self.get_ping_protocol_choices()
        self.time_between_pings.choices = self.get_time_between_pings_choices()
        self.failures_until_unhealthy.choices = self.get_failures_until_unhealthy_choices()
        self.passes_until_unhealthy.choices = self.get_passes_until_unhealthy_choices()

        # Set default choices where applicable, defaulting to first non-blank choice
        if self.cloud_type == 'aws' and len(self.zone.choices) > 1:
            self.zone.data = self.zone.choices[1][0]
        # Set the defailt option to be the first choice
        if len(self.vpc_subnet.choices) > 1:
            self.vpc_subnet.data = self.vpc_subnet.choices[0][0]
        if len(self.vpc_network.choices) > 1:
            self.vpc_network.data = self.vpc_network.choices[0][0]

    def set_error_messages(self):
        self.name.error_msg = self.name_error_msg

    def get_availability_zone_choices(self, region):
        return self.choices_manager.availability_zones(region, add_blank=False)

    def get_ping_protocol_choices(self):
        return [
            ('HTTP', 'HTTP'),
            ('HTTPS', 'HTTPS'),
            ('SSL', 'SSL'),
            ('TCP', 'TCP')
        ]

    def get_time_between_pings_choices(self):
        return [
            ('30', '30 seconds'),
            ('60', '1 minute'),
            ('300', '5 minutes')
        ]

    def get_failures_until_unhealthy_choices(self):
        return [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9'),
            ('10', '10'),
        ]

    def get_passes_until_unhealthy_choices(self):
        return [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9'),
            ('10', '10'),
        ]
