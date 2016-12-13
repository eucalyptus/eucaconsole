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
Forms for VPC resources

"""
from wtforms import SelectField

from ..i18n import _
from . import BaseSecureForm, ChoicesManager, TextEscapedField


class VPCsFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""

    def __init__(self, request, ec2_conn=None, cloud_type='euca', **kwargs):
        super(VPCsFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.cloud_type = cloud_type
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        self.facets = [
            {'name': 'state', 'label': _('State'), 'options': self.get_state_choices()},
            {'name': 'availability_zone', 'label': _('Availability zone'),
                'options': self.get_availability_zone_choices()},
        ]

    @staticmethod
    def get_state_choices():
        return [
            {'key': 'available', 'label': _(u'Available')},
            {'key': 'pending', 'label': _(u'Pending')},
        ]

    def get_availability_zone_choices(self):
        return self.get_options_from_choices(self.ec2_choices_manager.availability_zones(self.region, add_blank=False))


class VPCForm(BaseSecureForm):
    """VPC form (to update an existing VPC)"""
    name_error_msg = _(u'Not a valid name')
    name = TextEscapedField(label=_(u'Name'))
    internet_gateway = SelectField(label=_('Internet gateway'))

    def __init__(self, request, vpc_conn=None, vpc=None, vpc_internet_gateway=None, **kwargs):
        super(VPCForm, self).__init__(request, **kwargs)
        self.vpc_conn = vpc_conn
        self.vpc = vpc
        self.name.error_msg = self.name_error_msg
        vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.internet_gateway.choices = vpc_choices_manager.internet_gateways()

        if vpc is not None:
            self.name.data = vpc.tags.get('Name', '')
            if vpc_internet_gateway is not None:
                self.internet_gateway.data = vpc_internet_gateway.id


class VPCMainRouteTableForm(BaseSecureForm):
    """VPC form to set main route table"""
    route_table = SelectField(label=_('Route table'))

    def __init__(self, request, vpc_conn=None, vpc=None, vpc_main_route_table=None, **kwargs):
        super(VPCMainRouteTableForm, self).__init__(request, **kwargs)
        vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.route_table.choices = vpc_choices_manager.vpc_route_tables(vpc=vpc, add_blank=False)

        if vpc_main_route_table is not None:
            self.route_table.data = vpc_main_route_table.id
