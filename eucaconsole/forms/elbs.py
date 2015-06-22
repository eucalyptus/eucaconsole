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
import re
import wtforms
from wtforms import validators

from ..i18n import _
from . import BaseSecureForm, ChoicesManager, TextEscapedField, NAME_WITHOUT_SPACES_NOTICE, BLANK_CHOICE
from ..views import BaseView


NO_CERTIFICATES_CHOICE = ('None', _(u'There are no certificates available'))


class PingPathRequired(validators.Required):
    """Ping path is conditionally required based on protocol value"""

    def __init__(self, *args, **kwargs):
        super(PingPathRequired, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        if form.ping_protocol.data in ['HTTP', 'HTTPS']:
            super(PingPathRequired, self).__call__(form, field)


class CertificateARNRequired(validators.Required):
    """Custom validator to conditionally require certificate_arn when certificate_name is missing"""

    def __init__(self, *args, **kwargs):
        super(CertificateARNRequired, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        if not form.certificate_name.data:
            super(CertificateARNRequired, self).__call__(form, field)


class ELBForm(BaseSecureForm):
    """Elastic Load Balancer update form (General tab)"""
    idle_timeout = wtforms.IntegerField(
        label=_(u'Idle timeout (secs)'),
    )
    idle_timeout_help_text = _(u'Amount of time a connection to an instance can be idle \
                                 before the load balancer closes it. If keep alive is set for instances, \
                                 keep alive value should be set higher than idle timeout.')
    securitygroup_error_msg = _(u'Security groups are required')
    securitygroup = wtforms.SelectMultipleField(
        label=_(u'Security groups'),
    )

    def __init__(self, request, conn=None, vpc_conn=None, elb=None, securitygroups=None, **kwargs):
        super(ELBForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.vpc_conn = vpc_conn
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        self.security_groups = securitygroups or []
        self.idle_timeout.help_text = self.idle_timeout_help_text
        self.set_error_messages()
        self.set_choices()
        if elb is not None:
            self.idle_timeout.data = self.get_idle_timeout(elb)

    def set_error_messages(self):
        self.securitygroup.error_msg = self.securitygroup_error_msg

    def set_choices(self):
        self.securitygroup.choices = self.set_security_group_choices()

    def set_security_group_choices(self):
        choices = []
        for sgroup in self.security_groups:
            sg_name = sgroup.name
            sg_name = BaseView.escape_braces(sg_name)
            choices.append((sgroup.id, sg_name))
        if not self.security_groups:
            choices.append(('default', 'default'))
        return sorted(set(choices))

    @staticmethod
    def get_idle_timeout(elb=None):
        if hasattr(elb, 'idle_timeout'):
            return elb.idle_timeout
        if elb:
            elb_attrs = elb.get_attributes()
            if elb_attrs:
                return elb_attrs.connecting_settings.idle_timeout


class ELBHealthChecksForm(BaseSecureForm):
    """ELB Health Checks form"""
    ping_protocol_error_msg = _(u'Ping protocol is required')
    ping_protocol = wtforms.SelectField(
        label=_(u'Protocol'),
        validators=[validators.InputRequired(message=ping_protocol_error_msg)],
    )
    ping_port_error_msg = _(u'Port range value must be whole numbers between 1-65535')
    ping_port = wtforms.IntegerField(
        label=_(u'Port'),
        validators=[
            validators.InputRequired(message=ping_port_error_msg),
            validators.NumberRange(min=1, max=65535),
        ],
    )
    ping_path_error_msg = _(u'Ping path is required')
    ping_path = TextEscapedField(
        id=u'ping-path',
        label=_(u'Path'),
        default="index.html",
        validators=[PingPathRequired(message=ping_path_error_msg)],
    )
    response_timeout_error_msg = _(u'Response timeout is required')
    response_timeout = wtforms.IntegerField(
        label=_(u'Response timeout (secs)'),
        validators=[validators.InputRequired(message=response_timeout_error_msg)],
    )
    time_between_pings_error_msg = _(u'Time between pings is required')
    time_between_pings = wtforms.SelectField(
        label=_(u'Time between pings'),
        validators=[validators.InputRequired(message=time_between_pings_error_msg)],
    )
    failures_until_unhealthy_error_msg = _(u'Failures until unhealthy is required')
    failures_until_unhealthy = wtforms.SelectField(
        label=_(u'Failures until unhealthy'),
        validators=[validators.InputRequired(message=failures_until_unhealthy_error_msg)],
    )
    passes_until_healthy_error_msg = _(u'Passes until healthy is required')
    passes_until_healthy = wtforms.SelectField(
        label=_(u'Passes until healthy'),
        validators=[validators.InputRequired(message=passes_until_healthy_error_msg)],
    )

    def __init__(self, request, elb=None, **kwargs):
        super(ELBHealthChecksForm, self).__init__(request, **kwargs)
        self.elb = elb
        self.set_error_messages()
        self.set_choices()
        self.set_initial_data()

    def set_initial_data(self):
        if self.elb:
            hc_data = self.get_health_check_data()
            self.ping_protocol.data = hc_data.get('ping_protocol')
            self.ping_port.data = int(hc_data.get('ping_port', 80))
            self.ping_path.data = hc_data.get('ping_path')
            self.time_between_pings.data = str(self.elb.health_check.interval)
            self.response_timeout.data = self.elb.health_check.timeout
            self.failures_until_unhealthy.data = str(self.elb.health_check.unhealthy_threshold)
            self.passes_until_healthy.data = str(self.elb.health_check.healthy_threshold)

    def set_error_messages(self):
        self.ping_path.error_msg = self.ping_path_error_msg

    def set_choices(self):
        self.ping_protocol.choices = CreateELBForm.get_ping_protocol_choices()
        self.time_between_pings.choices = CreateELBForm.get_time_between_pings_choices()
        self.failures_until_unhealthy.choices = CreateELBForm.get_failures_until_unhealthy_choices()
        self.passes_until_healthy.choices = CreateELBForm.get_passes_until_healthy_choices()

    def get_health_check_data(self):
        if self.elb is not None and self.elb.health_check.target is not None:
            match = re.search('^(\w+):(\d+)/?(.+)?', self.elb.health_check.target)
            return dict(
                ping_protocol=match.group(1),
                ping_port=match.group(2),
                ping_path=match.group(3),
            )
        return {}


class ELBInstancesForm(BaseSecureForm):
    """ELB Instances form."""
    cross_zone_enabled_help_text = _(u'Distribute traffic evenly across all instances in all availability zones')
    cross_zone_enabled = wtforms.BooleanField(label=_(u'Enable cross-zone load balancing'))

    def __init__(self, request, elb=None, cross_zone_enabled=False, **kwargs):
        super(ELBInstancesForm, self).__init__(request, **kwargs)
        self.elb = elb
        self.cross_zone_enabled.data = cross_zone_enabled
        self.cross_zone_enabled.help_text = self.cross_zone_enabled_help_text


class ELBDeleteForm(BaseSecureForm):
    """ELB deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


class ELBsFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    availability_zones = wtforms.SelectMultipleField(label=_(u'Availability zone'))
    subnets = wtforms.SelectMultipleField(label=_(u'VPC subnet'))

    def __init__(self, request, cloud_type='euca', ec2_conn=None, vpc_conn=None, is_vpc_supported=False, **kwargs):
        super(ELBsFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.cloud_type = cloud_type
        self.vpc_conn = vpc_conn
        region = request.session.get('region')
        self.facets = []
        if is_vpc_supported:
            vpc_choices_manager = ChoicesManager(conn=self.vpc_conn)
            self.subnets.choices = vpc_choices_manager.vpc_subnets(add_blank=False, show_zone=True)
            self.facets.append(dict(
                name='subnet',
                label=self.subnets.label.text,
                options=self.getOptionsFromChoices(self.subnets.choices)
            ))
        else:
            ec2_choices_manager = ChoicesManager(conn=ec2_conn)
            self.availability_zones.choices = ec2_choices_manager.availability_zones(region, add_blank=False)
            self.facets.append(dict(
                name='availability_zone',
                label=self.availability_zones.label.text,
                options=self.getOptionsFromChoices(self.availability_zones.choices)
            ))


class CreateELBForm(BaseSecureForm):
    """Create Elastic Load Balancer form"""
    name_error_msg = NAME_WITHOUT_SPACES_NOTICE
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.InputRequired(message=name_error_msg)],
    )
    vpc_network_error_msg = _(u'VPC network is required')
    vpc_network = wtforms.SelectField(
        label=_(u'VPC network'),
        validators=[validators.InputRequired(message=vpc_network_error_msg)],
    )
    vpc_subnet = wtforms.SelectMultipleField(
        label=_(u'VPC subnets'),
    )
    securitygroup_error_msg = _(u'Security group is required')
    securitygroup = wtforms.SelectMultipleField(
        label=_(u'Security groups'),
        validators=[validators.InputRequired(message=securitygroup_error_msg)],
    )
    zone = wtforms.SelectMultipleField(
        label=_(u'Availability zones'),
    )
    cross_zone_enabled_help_text = _(u'Distribute traffic evenly across all instances in all availability zones')
    cross_zone_enabled = wtforms.BooleanField(label=_(u'Enable cross-zone load balancing'))
    add_availability_zones_help_text = _(
        u'Enable this load balancer to route traffic to instances in the selected zones')
    add_vpc_subnets_help_text = _(u'Enable this load balancer to route traffic to instances in the selected subnets')
    add_instances_help_text = _(u'Balance traffic between the selected instances')
    ping_protocol_error_msg = _(u'Ping protocol is required')
    ping_protocol = wtforms.SelectField(
        label=_(u'Protocol'),
        validators=[validators.InputRequired(message=ping_protocol_error_msg)],
    )
    ping_port_error_msg = _(u'Port range value must be whole numbers between 1-65535')
    ping_port = wtforms.IntegerField(
        label=_(u'Port'),
        validators=[
            validators.InputRequired(message=ping_port_error_msg),
            validators.NumberRange(min=1, max=65535),
        ],
    )
    ping_path_error_msg = _(u'Ping path is required')
    ping_path = TextEscapedField(
        id=u'ping-path',
        label=_(u'Path'),
        default="index.html",
        validators=[validators.InputRequired(message=ping_path_error_msg)],
    )
    response_timeout_error_msg = _(u'Response timeout is required')
    response_timeout = wtforms.IntegerField(
        label=_(u'Response timeout (secs)'),
        validators=[validators.InputRequired(message=response_timeout_error_msg)],
    )
    time_between_pings_error_msg = _(u'Time between pings is required')
    time_between_pings = wtforms.SelectField(
        label=_(u'Time between pings'),
        validators=[validators.InputRequired(message=time_between_pings_error_msg)],
    )
    failures_until_unhealthy_error_msg = _(u'Failures until unhealthy is required')
    failures_until_unhealthy = wtforms.SelectField(
        label=_(u'Failures until unhealthy'),
        validators=[validators.InputRequired(message=failures_until_unhealthy_error_msg)],
    )
    passes_until_healthy_error_msg = _(u'Passes until healthy is required')
    passes_until_healthy = wtforms.SelectField(
        label=_(u'Passes until healthy'),
        validators=[validators.InputRequired(message=passes_until_healthy_error_msg)],
    )

    def __init__(self, request, conn=None, vpc_conn=None, **kwargs):
        super(CreateELBForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.vpc_conn = vpc_conn
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        self.set_error_messages()
        self.choices_manager = ChoicesManager(conn=conn)
        self.vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.set_choices(request)
        self.cross_zone_enabled.help_text = self.cross_zone_enabled_help_text

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
        self.ping_protocol.choices = CreateELBForm.get_ping_protocol_choices()
        self.time_between_pings.choices = CreateELBForm.get_time_between_pings_choices()
        self.failures_until_unhealthy.choices = CreateELBForm.get_failures_until_unhealthy_choices()
        self.passes_until_healthy.choices = CreateELBForm.get_passes_until_healthy_choices()

        self.cross_zone_enabled.data = True
        # Set default choices where applicable, defaulting to first non-blank choice
        if self.cloud_type == 'aws' and len(self.zone.choices) > 1:
            self.zone.data = self.zone.choices[0]
        # Set the defailt option to be the first choice
        if len(self.vpc_network.choices) > 1:
            self.vpc_network.data = self.vpc_network.choices[0][0]

    def set_error_messages(self):
        self.name.error_msg = self.name_error_msg

    def get_availability_zone_choices(self, region):
        return self.choices_manager.availability_zones(region, add_blank=False)

    @staticmethod
    def get_ping_protocol_choices():
        return [
            ('HTTP', 'HTTP'),
            ('HTTPS', 'HTTPS'),
            ('TCP', 'TCP'),
            ('SSL', 'SSL')
        ]

    @staticmethod
    def get_time_between_pings_choices():
        return [
            ('30', _(u'30 seconds')),
            ('60', _(u'1 minute')),
            ('300', _(u'5 minutes'))
        ]

    @staticmethod
    def get_failures_until_unhealthy_choices():
        return [(str(x), str(x)) for x in range(2, 11)]

    @staticmethod
    def get_passes_until_healthy_choices():
        return [(str(x), str(x)) for x in range(2, 11)]


class ELBInstancesFiltersForm(BaseSecureForm):
    """Form class for filters on create ELB wizard"""
    state = wtforms.SelectMultipleField(label=_(u'Status'))
    availability_zone = wtforms.SelectMultipleField(label=_(u'Availability zone'))
    tags = TextEscapedField(label=_(u'Tags'))
    security_group = wtforms.SelectMultipleField(label=_(u'Security group'))
    vpc_id = wtforms.SelectMultipleField(label=_(u'VPC network'))
    subnet_id = wtforms.SelectMultipleField(label=_(u'VPC subnet'))

    def __init__(self, request, ec2_conn=None, autoscale_conn=None,
                 iam_conn=None, vpc_conn=None,
                 cloud_type='euca', **kwargs):
        super(ELBInstancesFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.cloud_type = cloud_type
        from ..views import BaseView
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        self.autoscale_choices_manager = ChoicesManager(conn=autoscale_conn)
        self.iam_choices_manager = ChoicesManager(conn=iam_conn)
        self.vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.region = request.session.get('region')
        self.availability_zone.choices = self.get_availability_zone_choices(self.region)
        self.state.choices = self.get_status_choices()
        self.security_group.choices = self.ec2_choices_manager.security_groups(add_blank=False)
        self.vpc_id.choices = self.vpc_choices_manager.vpc_networks(add_blank=False)
        if self.cloud_type == 'aws':
            self.vpc_id.choices.append(('None', _(u'No VPC')))
        self.vpc_id.choices = sorted(self.vpc_id.choices)
        self.subnet_id.choices = self.vpc_choices_manager.vpc_subnets(add_blank=False)
        self.facets = []
        self.set_search_facets()

    def set_search_facets(self):
        if self.cloud_type == 'aws':
            self.facets = [
                {'name': 'state', 'label': self.state.label.text, 'options': self.get_status_choices()},
                {'name': 'availability_zone', 'label': self.availability_zone.label.text,
                    'options': self.get_availability_zone_choices(self.region)},
                {'name': 'subnet_id', 'label': self.subnet_id.label.text,
                    'options': self.getOptionsFromChoices(self.vpc_choices_manager.vpc_subnets(add_blank=False))},
            ]
            vpc_choices = self.vpc_choices_manager.vpc_networks(add_blank=False)
            vpc_choices.append(('None', _(u'No VPC')))
        else:
            self.facets = [
                {'name': 'state', 'label': self.state.label.text, 'options': self.get_status_choices()},
            ]
            if self.is_vpc_supported:
                self.facets.append(
                    {'name': 'subnet_id', 'label': self.subnet_id.label.text,
                        'options': self.getOptionsFromChoices(self.vpc_choices_manager.vpc_subnets(add_blank=False))},
                )
            else:
                self.facets.append(
                    {'name': 'availability_zone', 'label': self.availability_zone.label.text,
                        'options': self.get_availability_zone_choices(self.region)},
                )

    def get_availability_zone_choices(self, region):
        return self.getOptionsFromChoices(self.ec2_choices_manager.availability_zones(region, add_blank=False))

    @staticmethod
    def get_status_choices():
        return [
            {'key': 'running', 'label': _(u'Running')},
            {'key': 'pending', 'label': _(u'Pending')},
            {'key': 'stopping', 'label': _(u'Stopping')},
            {'key': 'stopped', 'label': _(u'Stopped')},
            {'key': 'shutting-down', 'label': _(u'Terminating')},
            {'key': 'terminated', 'label': _(u'Terminated')},
        ]


class CertificateForm(BaseSecureForm):
    """ELB Certificate form (used on wizard and detail page)"""
    certificate_name_error_msg = NAME_WITHOUT_SPACES_NOTICE
    certificate_name = wtforms.TextField(
        label=_(u'Certificate name'),
        validators=[validators.InputRequired(message=certificate_name_error_msg)],
    )
    private_key_error_msg = _(u'Private key is required')
    private_key = wtforms.TextAreaField(
        label=_(u'Private key'),
        validators=[validators.InputRequired(message=private_key_error_msg)],
    )
    public_key_certificate_error_msg = _(u'Public key certificate is required')
    public_key_certificate = wtforms.TextAreaField(
        label=_(u'Public key certificate'),
        validators=[validators.InputRequired(message=public_key_certificate_error_msg)],
    )
    certificate_chain = wtforms.TextAreaField(
        label=_(u'Certificate chain'),
    )
    certificates_error_msg = _(u'Certificate is required')
    certificate_arn = wtforms.SelectField(
        label=_(u'Certificate'),
        validators=[CertificateARNRequired(message=certificates_error_msg)],
    )

    def __init__(self, request, conn=None, iam_conn=None, elb_conn=None, can_list_certificates=True, **kwargs):
        super(CertificateForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.iam_conn = iam_conn
        self.elb_conn = elb_conn
        self.can_list_certificates = can_list_certificates
        self.set_error_messages()
        self.set_certificate_choices()

    def set_error_messages(self):
        self.certificate_name.error_msg = self.certificate_name_error_msg
        self.private_key.error_msg = self.private_key_error_msg
        self.public_key_certificate.error_msg = self.public_key_certificate_error_msg

    def set_certificate_choices(self):
        if self.iam_conn and self.can_list_certificates:
            self.certificate_arn.choices = self.get_all_server_certs(iam_conn=self.iam_conn)
            if len(self.certificate_arn.choices) > 1:
                self.certificate_arn.data = self.certificate_arn.choices[0][0]
        else:
            self.certificate_arn.choices = []

    def get_all_server_certs(self,  iam_conn=None, add_blank=True):
        choices = []
        if iam_conn is not None:
            certificates = self.iam_conn.get_all_server_certs()
            for cert in certificates.list_server_certificates_result.server_certificate_metadata_list:
                choices.append((cert.arn, cert.server_certificate_name))
        if len(choices) == 0:
            choices.append(NO_CERTIFICATES_CHOICE)
        else:
            choices.insert(0, BLANK_CHOICE)
        return sorted(set(choices))


class BackendCertificateForm(BaseSecureForm):
    """ELB Backend Certificate form (used on wizard and detail page)"""
    backend_certificate_name_error_msg = NAME_WITHOUT_SPACES_NOTICE
    backend_certificate_name = wtforms.TextField(
        label=_(u'Certificate name'),
        validators=[validators.InputRequired(message=backend_certificate_name_error_msg)],
    )
    backend_certificate_body_error_msg = _(u'Backend certificate body is required')
    backend_certificate_body = wtforms.TextAreaField(
        label=_(u'Body (pem encoded)'),
        validators=[validators.InputRequired(message=backend_certificate_body_error_msg)],
    )

    def __init__(self, request, conn=None, iam_conn=None, elb_conn=None, **kwargs):
        super(BackendCertificateForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.iam_conn = iam_conn
        self.elb_conn = elb_conn
        self.set_error_messages()

    def set_error_messages(self):
        self.backend_certificate_name.error_msg = self.backend_certificate_name_error_msg
        self.backend_certificate_body.error_msg = self.backend_certificate_body_error_msg


class PredefinedPolicyRequired(validators.Required):
    """Custom validator to conditionally require predefined policy if custom policy isn't uploaded"""

    def __init__(self, *args, **kwargs):
        super(PredefinedPolicyRequired, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        conditions = [
            form.ssl_protocols.data,
            form.ssl_ciphers.data
        ]
        if not all(conditions):
            super(PredefinedPolicyRequired, self).__call__(form, field)


class SecurityPolicyForm(BaseSecureForm):
    """ELB Security Policy form"""
    predefined_policy_error_msg = _(u'Policy is required')
    predefined_policy = wtforms.SelectField(
        label=_(u'Policy name'),
        validators=[PredefinedPolicyRequired(message=predefined_policy_error_msg)],
        choices=[],
    )
    ssl_protocols = wtforms.SelectMultipleField(
        label=_(u'SSL Protocols'),
    )
    ssl_ciphers = wtforms.SelectMultipleField(
        label=_(u'SSL Ciphers'),
        choices=[],
    )
    ssl_options = wtforms.BooleanField(label=_(u'SSL Options'))

    def __init__(self, request, **kwargs):
        super(SecurityPolicyForm, self).__init__(request, **kwargs)
        self.set_error_messages()
        self.set_choices()

    def set_error_messages(self):
        self.predefined_policy.error_msg = self.predefined_policy_error_msg

    def set_choices(self):
        self.ssl_protocols.choices = self.get_ssl_protocol_choices()

    @staticmethod
    def get_ssl_protocol_choices():
        return [
            ('Protocol-TLSv1.2', u'TLSv1.2'),
            ('Protocol-TLSv1.1', u'TLSv1.1'),
            ('Protocol-TLSv1', u'TLSv1'),
        ]
