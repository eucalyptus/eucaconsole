# -*- coding: utf-8 -*-
# Copyright 2016 Hewlett Packard Enterprise Development LP
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
Pyramid views for Eucalyptus and AWS VPCs

"""
from pyramid.view import view_config

from ..forms import ChoicesManager 
from ..views import BaseView
from . import boto_error_handler


class VPCsJsonView(BaseView):
    def __init__(self, request):
        super(VPCsJsonView, self).__init__(request)
        self.conn = self.get_connection(conn_type='vpc')

    @view_config(route_name='vpcnetworks_json', renderer='json', request_method='GET')
    def vpcnetworks_json(self):
        with boto_error_handler(self.request):
            vpc_networks = ChoicesManager(self.conn).vpc_networks(add_blank=False)
            return dict(results=[dict(id=item[0], label=item[1]) for item in vpc_networks])

    @view_config(route_name='vpcsubnets_json', renderer='json', request_method='GET')
    def vpcsubnets_json(self):
        with boto_error_handler(self.request):
            vpc_subnets = ChoicesManager(self.conn).vpc_subnets(show_zone=True, add_blank=False)
            return dict(results=[dict(id=subnet[0], label=subnet[1]) for subnet in vpc_subnets])


class VPCSecurityGroupsJsonView(BaseView):
    def __init__(self, request):
        super(VPCSecurityGroupsJsonView, self).__init__(request)
        self.conn = self.get_connection()

    @view_config(route_name='vpcsecuritygroups_json', renderer='json', request_method='GET')
    def vpcsecuritygroups_json(self):
        with boto_error_handler(self.request):
            vpc_securitygroups = ChoicesManager(self.conn).security_groups(add_blank=False, use_id=True)
            return dict(results=[dict(id=item[0], label=item[1]) for item in vpc_securitygroups])
