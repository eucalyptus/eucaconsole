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
Forms for Security Groups

"""
import wtforms
from wtforms import validators

from ..i18n import _
from ..views import BaseView
from . import BaseSecureForm, ChoicesManager, TextEscapedField, ASCII_WITHOUT_SLASHES_NOTICE


class SecurityGroupForm(BaseSecureForm):
    """Security Group create/edit form
       Constraints for VPC security group name/desc: a-z, A-Z, 0-9, spaces, and ._-:/()#,@[]+=;{}!$*
       See http://docs.aws.amazon.com/cli/latest/reference/ec2/create-security-group.html
    """
    name_error_msg = ASCII_WITHOUT_SLASHES_NOTICE
    name = wtforms.TextField(
        label=_(u'Name'),
        validators=[validators.DataRequired(message=name_error_msg)],
    )
    sgroup_description_pattern = r'^[a-zA-Z0-9\s\._\-:\/\(\)#,@\[\]\+=;\{\}!\$\*]+$'
    DESCRIPTION_RESTRICTION_NOTICE = _(
        u'Description is required, must be between 1 and 255 characters, and may only contain '
        u'letters, numbers, spaces, and the following characters:')
    special_chars = u'._-:/()#,@[]+=;{}!$*'
    desc_error_msg = u'{0} {1}'.format(DESCRIPTION_RESTRICTION_NOTICE, special_chars)
    description = wtforms.TextAreaField(
        label=_(u'Description'),
        validators=[
            validators.DataRequired(message=desc_error_msg),
            validators.Length(max=255, message=_(u'Description must be less than 255 characters'))
        ],
    )
    securitygroup_vpc_network = wtforms.SelectField(label=_(u'VPC network'))

    def __init__(self, request, vpc_conn=None, security_group=None, **kwargs):
        super(SecurityGroupForm, self).__init__(request, **kwargs)
        self.vpc_conn = vpc_conn
        self.name.error_msg = self.name_error_msg  # Used for Foundation Abide error message
        self.description.error_msg = self.desc_error_msg  # Used for Foundation Abide error message
        self.vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.cloud_type = request.session.get('cloud_type', 'euca')
        from ..views import BaseView
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        self.set_vpc_choices()

        # Although we don't need to show the name/desc fields on update, we need these here to ensure the form is valid
        if security_group is not None:
            self.name.data = security_group.name
            self.description.data = security_group.description
            self.securitygroup_vpc_network.data = security_group.vpc_id or ''

    def set_vpc_choices(self):
        if self.cloud_type == 'euca' and self.is_vpc_supported:
            self.securitygroup_vpc_network.choices = self.vpc_choices_manager.vpc_networks(add_blank=False)
        else:
            self.securitygroup_vpc_network.choices = self.vpc_choices_manager.vpc_networks()


class SecurityGroupDeleteForm(BaseSecureForm):
    """Security Group deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


class SecurityGroupsFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    vpc_id = wtforms.SelectMultipleField(label=_(u'VPC network'))
    tags = TextEscapedField(label=_(u'Tags'))

    def __init__(self, request, vpc_conn=None, cloud_type='euca', **kwargs):
        super(SecurityGroupsFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.cloud_type = cloud_type
        self.vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.vpc_id.choices = self.vpc_choices_manager.vpc_networks(add_blank=False)
        if self.cloud_type == 'aws':
            self.vpc_id.choices.append(('None', _(u'No VPC')))
        self.vpc_id.choices = sorted(self.vpc_id.choices)
        self.facets = []
        if BaseView.is_vpc_supported(request):
            self.facets.append(
                {'name': 'vpc_id', 'label': self.vpc_id.label.text,
                    'options': self.get_options_from_choices(self.vpc_id.choices)}
            )
