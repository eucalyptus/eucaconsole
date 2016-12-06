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
import simplejson as json

from pyramid.view import view_config

from ..forms import ChoicesManager
from ..forms.vpcs import VPCsFiltersForm
from ..i18n import _
from ..views import BaseView, LandingPageView, TaggedItemView, JSONResponse
from . import boto_error_handler


class VPCsView(LandingPageView):
    TEMPLATE = '../templates/vpcs/vpcs.pt'

    def __init__(self, request):
        super(VPCsView, self).__init__(request)
        self.title_parts = [_(u'VPCs')]
        self.ec2_conn = self.get_connection()
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.location = self.get_redirect_location('vpcs')
        self.initial_sort_key = 'name'
        self.prefix = '/vpcs'
        self.json_items_endpoint = self.get_json_endpoint('vpcs_json')
        self.is_vpc_supported = BaseView.is_vpc_supported(request)
        self.enable_smart_table = True
        self.render_dict = dict(prefix=self.prefix)

    @view_config(route_name='vpcs', renderer=TEMPLATE)
    def vpcs_landing(self):
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = []
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='state', name=_(u'State')),
        ]
        filters_form = VPCsFiltersForm(self.request, ec2_conn=self.ec2_conn)
        self.render_dict.update(dict(
            filter_keys=self.filter_keys,
            search_facets=BaseView.escape_json(json.dumps(filters_form.facets)),
            sort_keys=self.sort_keys,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
        ))
        return self.render_dict


class VPCsJsonView(BaseView):
    def __init__(self, request):
        super(VPCsJsonView, self).__init__(request)
        self.vpc_conn = self.get_connection(conn_type='vpc')

    @view_config(route_name='vpcs_json', renderer='json', request_method='POST')
    def vpcs_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")

        with boto_error_handler(self.request):
            vpc_items = self.vpc_conn.get_all_vpcs() if self.vpc_conn else []
            subnets = self.vpc_conn.get_all_subnets()
            route_tables = self.vpc_conn.get_all_route_tables()
            internet_gateways = self.vpc_conn.get_all_internet_gateways()

        # Filter items based on MSB params
        zone = self.request.params.get('availability_zone')
        if zone:
            vpc_items = self.filter_vpcs_by_availability_zone(vpc_items, zone=zone)

        vpc_list = []
        for vpc in vpc_items:
            vpc_subnets = self.filter_subnets_by_vpc(subnets, vpc.id)
            availability_zones = [subnet.get('availability_zone') for subnet in vpc_subnets]
            vpc_route_tables = self.filter_route_tables_by_vpc(route_tables, vpc.id)
            vpc_internet_gateways = self.filter_internet_gateways_by_vpc(internet_gateways, vpc.id)
            vpc_list.append(dict(
                id=vpc.id,
                name=TaggedItemView.get_display_name(vpc),
                state=vpc.state,
                cidr_block=vpc.cidr_block,
                subnets=vpc_subnets,
                availability_zones=availability_zones,
                route_tables=vpc_route_tables,
                internet_gateways=vpc_internet_gateways,
                default_vpc=_('yes') if vpc.is_default else _('no'),
                tags=TaggedItemView.get_tags_display(vpc.tags),
            ))
        return dict(results=vpc_list)

    @staticmethod
    def filter_vpcs_by_availability_zone(vpc_items, zone=None):
        return [item for item in vpc_items if zone in item.availability_zones]

    @staticmethod
    def filter_subnets_by_vpc(subnets, vpc_id):
        subnet_list = []
        for subnet in subnets:
            if subnet.vpc_id == vpc_id:
                subnet_list.append(dict(
                    id=subnet.id,
                    name=TaggedItemView.get_display_name(subnet),
                    cidr_block=subnet.cidr_block,
                    availability_zone=subnet.availability_zone,
                ))
        return subnet_list

    @staticmethod
    def filter_route_tables_by_vpc(route_tables, vpc_id):
        rtables_list = []
        for rtable in route_tables:
            if rtable.vpc_id == vpc_id:
                rtables_list.append(dict(
                    id=rtable.id,
                    name=TaggedItemView.get_display_name(rtable),
                ))
        return rtables_list

    @staticmethod
    def filter_internet_gateways_by_vpc(internet_gateways, vpc_id):
        internet_gateways_list = []
        for igw in internet_gateways:
            for attachment in igw.attachments:
                if attachment.vpc_id == vpc_id:
                    internet_gateways_list.append(dict(
                        id=igw.id,
                        name=TaggedItemView.get_display_name(igw),
                    ))
        return internet_gateways_list


class VPCNetworksJsonView(BaseView):
    def __init__(self, request):
        super(VPCNetworksJsonView, self).__init__(request)
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
