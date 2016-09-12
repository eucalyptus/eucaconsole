# -*- coding: utf-8 -*-
# Copyright 2013-2016 Hewlett Packard Enterprise Development LP
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
from ..constants.elbs import SSL_CIPHERS
from ..views import BaseView


NO_CERTIFICATES_CHOICE = ('None', _(u'There are no certificates available'))


class PingPathRequired(validators.DataRequired):
    """Ping path is conditionally required based on protocol value"""

    def __init__(self, *args, **kwargs):
        super(PingPathRequired, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        if form.ping_protocol.data in ['HTTP', 'HTTPS']:
            super(PingPathRequired, self).__call__(form, field)


class BucketInfoRequired(validators.DataRequired):
    """Bucket info (name, interval) conditionally required based on logging_enabled value"""

    def __init__(self, *args, **kwargs):
        super(BucketInfoRequired, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        if form.logging_enabled.data:
            super(BucketInfoRequired, self).__call__(form, field)


class CertificateARNRequired(validators.DataRequired):
    """Custom validator to conditionally require certificate_arn when certificate_name is missing"""

    def __init__(self, *args, **kwargs):
        super(CertificateARNRequired, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        if not form.certificate_name.data:
            super(CertificateARNRequired, self).__call__(form, field)


class ELBAccessLogsFormMixin(object):
    PREFIX_PATTERN = '^[^A-Z]*$'
    logging_enabled = wtforms.BooleanField(label=_(u'Enable logging'))
    bucket_name_error_msg = _(u'Bucket name is required')
    bucket_name_help_text = _(u'Choose from your existing buckets, or create a new bucket.')
    bucket_name = wtforms.SelectField(
        label=_(u'Bucket name'),
        validators=[BucketInfoRequired(message=bucket_name_error_msg)],
    )
    bucket_prefix_help_text = _(
        u"The path where log files will be stored within the bucket. "
        u"If not specified, logs will be created at the bucket's root level")
    bucket_prefix = TextEscapedField(label=_(u'Prefix'))
    bucket_prefix_error_msg = _(u'Prefix may not contain uppercase letters')
    collection_interval = wtforms.SelectField(
        label=_(u'Collection interval'),
    )

    def set_access_logs_initial_data(self):
        if not self.kwargs.get('formdata'):
            access_logs = self.elb_conn.get_lb_attribute(self.elb.name, 'accessLog')
            self.logging_enabled.data = access_logs.enabled
            self.bucket_name.data = access_logs.s3_bucket_name
            self.bucket_prefix.data = access_logs.s3_bucket_prefix
            self.collection_interval.data = '5' if access_logs.emit_interval == 5 else '60'

    @staticmethod
    def get_collection_interval_choices():
        return [
            (u'60', _(u'60 minutes')),
            (u'5', _(u'5 minutes')),
        ]


class ELBForm(BaseSecureForm, ELBAccessLogsFormMixin):
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

    def __init__(self, request, conn=None, vpc_conn=None, elb=None, elb_conn=None, s3_conn=None,
                 securitygroups=None, **kwargs):
        super(ELBForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.vpc_conn = vpc_conn
        self.elb_conn = elb_conn
        self.elb = elb
        self.kwargs = kwargs
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        self.security_groups = securitygroups or []
        self.s3_choices_manager = ChoicesManager(conn=s3_conn)
        self.idle_timeout.help_text = self.idle_timeout_help_text
        self.set_error_messages()
        self.set_choices()
        self.set_help_text()
        self.set_access_logs_initial_data()
        if elb is not None:
            self.idle_timeout.data = self.get_idle_timeout(elb)

    def set_error_messages(self):
        self.securitygroup.error_msg = self.securitygroup_error_msg
        self.bucket_name.error_msg = self.bucket_name_error_msg
        self.bucket_prefix.error_msg = self.bucket_prefix_error_msg

    def set_choices(self):
        self.securitygroup.choices = self.set_security_group_choices()
        self.bucket_name.choices = self.s3_choices_manager.buckets()
        self.collection_interval.choices = self.get_collection_interval_choices()

    def set_help_text(self):
        self.bucket_name.help_text = self.bucket_name_help_text
        self.bucket_prefix.help_text = self.bucket_prefix_help_text

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
    ping_path_error_msg = _(u'Ping path is required and must start with a /')
    ping_path = TextEscapedField(
        id=u'ping-path',
        label=_(u'Path'),
        default="/",
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

    def __init__(self, request, s3_conn=None, elb_conn=None, elb=None, **kwargs):
        super(ELBHealthChecksForm, self).__init__(request, **kwargs)
        self.s3_conn = s3_conn
        self.s3_choices_manager = ChoicesManager(conn=s3_conn)
        self.elb_conn = elb_conn
        self.elb = elb
        self.kwargs = kwargs
        self.set_health_check_initial_data()
        self.set_health_check_choices()
        self.set_health_check_error_messages()

    def set_health_check_initial_data(self):
        if self.elb is not None:
            # Set health check initial data
            hc_data = self.get_health_check_data()
            self.ping_protocol.data = hc_data.get('ping_protocol')
            self.ping_port.data = int(hc_data.get('ping_port', 80))
            self.ping_path.data = hc_data.get('ping_path')
            self.time_between_pings.data = str(self.elb.health_check.interval)
            self.response_timeout.data = self.elb.health_check.timeout
            self.failures_until_unhealthy.data = str(self.elb.health_check.unhealthy_threshold)
            self.passes_until_healthy.data = str(self.elb.health_check.healthy_threshold)

    def set_health_check_error_messages(self):
        self.ping_path.error_msg = self.ping_path_error_msg

    def set_health_check_choices(self):
        self.ping_protocol.choices = self.get_ping_protocol_choices()
        self.time_between_pings.choices = self.get_time_between_pings_choices()
        self.failures_until_unhealthy.choices = self.get_failures_until_unhealthy_choices()
        self.passes_until_healthy.choices = self.get_passes_until_healthy_choices()

    def get_health_check_data(self):
        if self.elb is not None and self.elb.health_check.target is not None:
            match = re.search('^(\w+):(\d+)(.+)?', self.elb.health_check.target)
            return dict(
                ping_protocol=match.group(1),
                ping_port=match.group(2),
                ping_path=match.group(3),
            )
        return {}

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
        self.facets = []
        if is_vpc_supported:
            vpc_choices_manager = ChoicesManager(conn=self.vpc_conn)
            self.subnets.choices = vpc_choices_manager.vpc_subnets(add_blank=False, show_zone=True)
            self.facets.append(dict(
                name='subnet',
                label=self.subnets.label.text,
                options=self.get_options_from_choices(self.subnets.choices)
            ))
        else:
            ec2_choices_manager = ChoicesManager(conn=ec2_conn)
            self.availability_zones.choices = ec2_choices_manager.availability_zones(self.region, add_blank=False)
            self.facets.append(dict(
                name='availability_zones',
                label=self.availability_zones.label.text,
                options=self.get_options_from_choices(self.availability_zones.choices)
            ))


class CreateELBForm(ELBHealthChecksForm, ELBAccessLogsFormMixin):
    """Create Elastic Load Balancer form"""
    ELB_NAME_PATTERN = '^[a-zA-Z0-9-]{1,32}$'
    name_error_msg = _(
        'Name is required, and may only contain alphanumeric characters and/or hyphens. '
        'Length may not exceed 32 characters.')
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
    securitygroup = wtforms.SelectMultipleField(
        label=_(u'Security groups')
    )
    securitygroup_help_text = _(u'If you do not select a security group, the default group will be used.')
    zone = wtforms.SelectMultipleField(
        label=_(u'Availability zones')
    )
    cross_zone_enabled_help_text = _(u'Distribute traffic evenly across all instances in all availability zones')
    cross_zone_enabled = wtforms.BooleanField(label=_(u'Enable cross-zone load balancing'))
    add_availability_zones_help_text = _(
        u'Enable this load balancer to route traffic to instances in the selected zones')
    add_vpc_subnets_help_text = _(u'Enable this load balancer to route traffic to instances in the selected subnets')
    add_instances_help_text = _(u'Balance traffic between the selected instances')

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
        # self.securitygroup.help_text = self.securitygroup_help_text
        self.cross_zone_enabled.help_text = self.cross_zone_enabled_help_text
        self.bucket_name.help_text = self.bucket_name_help_text
        self.bucket_prefix.help_text = self.bucket_prefix_help_text

    def set_choices(self, request):
        if self.cloud_type == 'euca' and self.is_vpc_supported:
            self.vpc_network.choices = self.vpc_choices_manager.vpc_networks(add_blank=False)
        else:
            self.vpc_network.choices = self.vpc_choices_manager.vpc_networks()
        self.vpc_subnet.choices = self.vpc_choices_manager.vpc_subnets()
        self.securitygroup.choices = self.choices_manager.security_groups(
            securitygroups=None, use_id=True, add_blank=False)
        self.zone.choices = self.get_availability_zone_choices()
        self.ping_protocol.choices = self.get_ping_protocol_choices()
        self.time_between_pings.choices = self.get_time_between_pings_choices()
        self.failures_until_unhealthy.choices = self.get_failures_until_unhealthy_choices()
        self.passes_until_healthy.choices = self.get_passes_until_healthy_choices()
        self.bucket_name.choices = self.s3_choices_manager.buckets()
        self.collection_interval.choices = self.get_collection_interval_choices()
        self.cross_zone_enabled.data = True
        # Set default choices where applicable, defaulting to first non-blank choice
        if self.cloud_type == 'aws' and len(self.zone.choices) > 1:
            self.zone.data = self.zone.choices[0]
        # Set the defailt option to be the first choice
        if len(self.vpc_network.choices) > 1:
            self.vpc_network.data = self.vpc_network.choices[0][0]

    def set_error_messages(self):
        self.name.error_msg = self.name_error_msg
        self.bucket_name.error_msg = self.bucket_name_error_msg
        self.bucket_prefix.error_msg = self.bucket_prefix_error_msg

    def get_availability_zone_choices(self):
        return self.choices_manager.availability_zones(self.region, add_blank=False)


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
                    'options': self.get_options_from_choices(self.vpc_choices_manager.vpc_subnets(add_blank=False))},
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
                        'options': self.get_options_from_choices(self.vpc_choices_manager.vpc_subnets(add_blank=False))},
                )
            else:
                self.facets.append(
                    {'name': 'availability_zone', 'label': self.availability_zone.label.text,
                        'options': self.get_availability_zone_choices(self.region)},
                )

    def get_availability_zone_choices(self, region):
        return self.get_options_from_choices(self.ec2_choices_manager.availability_zones(region, add_blank=False))

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
    private_key_help_text = _(
        u'Enter the contents of your private key file. Begins with Private-Key:')
    private_key = wtforms.TextAreaField(
        label=_(u'Private key'),
        validators=[validators.InputRequired(message=private_key_error_msg)],
    )
    public_key_certificate_error_msg = _(u'Public key certificate is required')
    public_key_help_text = _(
        u'Enter the contents of your public key certificate file. Begins with -----BEGIN CERTIFICATE-----'
    )
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
        self.set_help_text()
        self.set_certificate_choices()

    def set_error_messages(self):
        self.certificate_name.error_msg = self.certificate_name_error_msg
        self.private_key.error_msg = self.private_key_error_msg
        self.public_key_certificate.error_msg = self.public_key_certificate_error_msg

    def set_help_text(self):
        self.private_key.help_text = self.private_key_help_text
        self.public_key_certificate.help_text = self.public_key_help_text

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
        self.backend_certificate_body.help_text = CertificateForm.public_key_help_text

    def set_error_messages(self):
        self.backend_certificate_name.error_msg = self.backend_certificate_name_error_msg
        self.backend_certificate_body.error_msg = self.backend_certificate_body_error_msg


class PredefinedPolicyRequired(validators.DataRequired):
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
    )
    ssl_protocols_error_msg = _(u'At least one protocol is required.')
    ssl_protocols = wtforms.SelectMultipleField(
        label=_(u'SSL Protocols'),
        validators=[validators.InputRequired(message=ssl_protocols_error_msg)],
    )
    ssl_ciphers_error_msg = _(u'At least one cipher is required.')
    ssl_ciphers = wtforms.SelectMultipleField(
        label=_(u'SSL Ciphers'),
        validators=[validators.InputRequired(message=ssl_ciphers_error_msg)],
    )
    server_order_preference = wtforms.BooleanField(label=_(u'Server order preference'))  # Under SSL Options

    def __init__(self, request, elb_conn=None, predefined_policy_choices=None, **kwargs):
        super(SecurityPolicyForm, self).__init__(request, **kwargs)
        self.elb_conn = elb_conn
        self.predefined_policy_choices = predefined_policy_choices
        self.set_error_messages()
        self.set_choices()
        self.set_initial_data()

    def set_error_messages(self):
        self.predefined_policy.error_msg = self.predefined_policy_error_msg
        self.ssl_protocols.error_msg = self.ssl_protocols_error_msg
        self.ssl_ciphers.error_msg = self.ssl_ciphers_error_msg

    def set_choices(self):
        self.ssl_protocols.choices = self.get_ssl_protocol_choices()
        self.ssl_ciphers.choices = self.get_ssl_cipher_choices()
        self.predefined_policy.choices = self.get_predefined_policy_choices()

    def set_initial_data(self):
        # Default to TLS 1, 1.1, and 1.2 for ssl_protocols
        self.ssl_protocols.data = [val for val, label in self.get_ssl_protocol_choices()]

    def get_predefined_policy_choices(self):
        if self.predefined_policy_choices:
            return self.predefined_policy_choices
        if self.elb_conn is not None:
            return ChoicesManager(conn=self.elb_conn).predefined_policy_choices(add_blank=False)
        return []

    @staticmethod
    def get_ssl_protocol_choices():
        return [
            ('Protocol-TLSv1.2', u'TLSv1.2'),
            ('Protocol-TLSv1.1', u'TLSv1.1'),
            ('Protocol-TLSv1', u'TLSv1'),
        ]

    @staticmethod
    def get_ssl_cipher_choices():
        return [(val, val) for val in SSL_CIPHERS]
