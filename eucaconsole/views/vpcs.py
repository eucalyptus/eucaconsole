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

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config

from ..forms import ChoicesManager
from ..forms.vpcs import (
    VPCsFiltersForm, VPCForm, VPCMainRouteTableForm, CreateInternetGatewayForm,
    CreateVPCForm, VPCDeleteForm, INTERNET_GATEWAY_HELP_TEXT
)
from ..i18n import _
from ..models import Notification
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
        self.filter_keys = ['state']
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

        # Filter items based on MSB params
        zone = self.request.params.get('availability_zone')
        if zone:
            vpc_items = self.filter_vpcs_by_availability_zone(vpc_items, zone=zone)

        vpc_ids = [vpc.id for vpc in vpc_items]
        with boto_error_handler(self.request):
            subnets = self.vpc_conn.get_all_subnets(filters={'vpc-id': vpc_ids})
            main_route_tables = self.vpc_conn.get_all_route_tables(filters={'association.main': 'true'})
            internet_gateways = self.vpc_conn.get_all_internet_gateways(filters={'attachment.vpc-id': vpc_ids})

        vpc_list = []
        for vpc in vpc_items:
            vpc_subnets = self.filter_subnets_by_vpc(subnets, vpc.id)
            availability_zones = [subnet.get('availability_zone') for subnet in vpc_subnets]
            vpc_main_route_table = self.get_main_route_table_for_vpc(main_route_tables, vpc.id)
            vpc_internet_gateway = self.get_internet_gateway_for_vpc(internet_gateways, vpc.id)
            vpc_list.append(dict(
                id=vpc.id,
                name=TaggedItemView.get_display_name(vpc),
                state=vpc.state,
                cidr_block=vpc.cidr_block,
                subnets=vpc_subnets,
                availability_zones=availability_zones,
                main_route_table=vpc_main_route_table,
                internet_gateway=vpc_internet_gateway,
                default_vpc=_('Yes') if vpc.is_default else _('No'),
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
    def get_main_route_table_for_vpc(route_tables, vpc_id):
        for rtable in route_tables:
            if rtable.vpc_id == vpc_id:
                return dict(
                    id=rtable.id,
                    name=TaggedItemView.get_display_name(rtable),
                )
        return None

    @staticmethod
    def get_internet_gateway_for_vpc(internet_gateways, vpc_id):
        for igw in internet_gateways:
            for attachment in igw.attachments:
                if attachment.vpc_id == vpc_id:
                    return dict(
                        id=igw.id,
                        name=TaggedItemView.get_display_name(igw),
                    )
        return None


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


class VPCView(TaggedItemView):
    VIEW_TEMPLATE = '../templates/vpcs/vpc_view.pt'

    def __init__(self, request, **kwargs):
        super(VPCView, self).__init__(request, **kwargs)
        self.location = self.request.route_path('vpc_view', id=self.request.matchdict.get('id'))
        with boto_error_handler(request, self.location):
            self.conn = self.get_connection()
            self.vpc_conn = self.get_connection(conn_type='vpc')
            self.vpc = self.get_vpc()
            self.vpc_default_security_group = self.get_default_security_group()
            self.vpc_main_route_table = self.get_main_route_table()
            self.vpc_internet_gateway = self.get_internet_gateway()
            self.vpc_form = VPCForm(
                self.request, vpc=self.vpc, vpc_conn=self.vpc_conn,
                vpc_internet_gateway=self.vpc_internet_gateway, formdata=self.request.params or None)
            self.vpc_main_route_table_form = VPCMainRouteTableForm(
                self.request, vpc=self.vpc, vpc_conn=self.vpc_conn,
                vpc_main_route_table=self.vpc_main_route_table, formdata=self.request.params or None)
            self.create_internet_gateway_form = CreateInternetGatewayForm(
                self.request, formdata=self.request.params or None)
        self.vpc_delete_form = VPCDeleteForm(self.request, formdata=self.request.params or None)
        self.vpc_name = self.get_display_name(self.vpc)
        self.tagged_obj = self.vpc
        self.title_parts = [_(u'VPC'), self.vpc_name]
        self.render_dict = dict(
            vpc=self.vpc,
            vpc_name=self.vpc_name,
            vpc_form=self.vpc_form,
            vpc_delete_form=self.vpc_delete_form,
            vpc_main_route_table_form=self.vpc_main_route_table_form,
            create_internet_gateway_form=self.create_internet_gateway_form,
            internet_gateway_help_text=INTERNET_GATEWAY_HELP_TEXT,
            max_subnet_instance_count=10,  # Determines when to link to instances landing page in VPC subnets table
            vpc_default_security_group=self.vpc_default_security_group,
            vpc_main_route_table_name=TaggedItemView.get_display_name(
                self.vpc_main_route_table) if self.vpc_main_route_table else '',
            vpc_internet_gateway_name=TaggedItemView.get_display_name(
                self.vpc_internet_gateway) if self.get_internet_gateway() else '',
            default_vpc=self.vpc.is_default,
            default_vpc_label=_('Yes') if self.vpc.is_default else _('No'),
            tags=self.serialize_tags(self.vpc.tags) if self.vpc else [],
        )

    @view_config(route_name='vpc_view', renderer=VIEW_TEMPLATE, request_method='GET')
    def vpc_view(self):
        if self.vpc is None:
            raise HTTPNotFound()
        self.render_dict.update({
            'vpc_subnets': self.get_vpc_subnets()
        })
        return self.render_dict

    @view_config(route_name='vpc_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def vpc_update(self):
        if self.vpc and self.vpc_form.validate():
            location = self.request.route_path('vpc_view', id=self.vpc.id)
            with boto_error_handler(self.request, location):
                # Update tags
                self.update_tags()

                # Save Name tag
                name = self.request.params.get('name', '')
                self.update_name_tag(name)

                # Handle internet gateway update
                self.update_internet_gateway()

            msg = _(u'Successfully updated VPC')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.vpc_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='vpc_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def vpc_delete(self):
        if self.vpc and self.vpc_delete_form.validate():
            location = self.request.route_path('vpcs')
            deleted_vpc_name = TaggedItemView.get_display_name(self.vpc)
            with boto_error_handler(self.request, location):
                # Detach IGW if present
                if self.vpc_internet_gateway:
                    self.vpc_conn.detach_internet_gateway(self.vpc_internet_gateway.id, self.vpc.id)
                self.vpc_conn.delete_vpc(self.vpc.id)
            msg = _(u'Successfully deleted VPC {0}').format(deleted_vpc_name)
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.vpc_delete_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='vpc_set_main_route_table', renderer=VIEW_TEMPLATE, request_method='POST')
    def vpc_set_main_route_table(self):
        if self.vpc and self.vpc_main_route_table_form.validate():
            selected_route_table_id = self.vpc_main_route_table_form.route_table.data
            if self.vpc_main_route_table:
                existing_main_table_associations = [
                    assoc for assoc in self.vpc_main_route_table.associations if assoc.main is True]
                if existing_main_table_associations:
                    existing_assocation_id = existing_main_table_associations[0].id
                    with boto_error_handler(self.request, self.location):
                        self.vpc_conn.replace_route_table_association_with_assoc(
                            association_id=existing_assocation_id, route_table_id=selected_route_table_id)
            msg = _(u'Successfully set main route table for VPC')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        else:
            self.request.error_messages = self.vpc_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='vpc_create_internet_gateway', renderer='json', request_method='POST')
    def vpc_create_internet_gateway(self):
        location = self.request.route_path('vpc_view', id=self.vpc.id)
        if self.create_internet_gateway_form.validate():
            name = self.request.params.get('new_igw_name')
            with boto_error_handler(self.request):
                new_igw = self.vpc_conn.create_internet_gateway()
                if name:
                    new_igw.add_tag('Name', name)
            msg = _(u'Successfully created internet gateway')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            self.request.error_messages = ', '.join(self.create_internet_gateway_form.get_errors_list())
        return HTTPFound(location=location)

    def get_vpc(self):
        vpc_id = self.request.matchdict.get('id')
        if vpc_id:
            vpcs_list = self.vpc_conn.get_all_vpcs(vpc_ids=[vpc_id])
            return vpcs_list[0] if vpcs_list else None
        return None

    def get_vpc_subnets(self):
        subnets_list = []
        vpc_subnets = self.vpc_conn.get_all_subnets(filters={'vpc-id': [self.vpc.id]})
        vpc_route_tables = self.vpc_conn.get_all_route_tables(filters={'vpc-id': [self.vpc.id]})
        vpc_network_acls = self.vpc_conn.get_all_network_acls(filters={'vpc-id': [self.vpc.id]})
        vpc_reservations = self.conn.get_all_reservations(filters={'vpc-id': [self.vpc.id]})
        for subnet in vpc_subnets:
            instances = self.get_subnet_instances(subnet_id=subnet.id, vpc_reservations=vpc_reservations)
            subnets_list.append(dict(
                id=subnet.id,
                name=TaggedItemView.get_display_name(subnet),
                state=subnet.state,
                cidr_block=subnet.cidr_block,
                zone=subnet.availability_zone,
                available_ips=subnet.available_ip_address_count,
                instances=instances,
                instance_count=len(instances),
                route_tables=self.get_subnet_route_tables(subnet_id=subnet.id, vpc_route_tables=vpc_route_tables),
                network_acls=self.get_subnet_network_acls(subnet_id=subnet.id, vpc_network_acls=vpc_network_acls),
            ))
        return subnets_list

    def get_subnet_instances(self, subnet_id=None, vpc_reservations=None):
        instances = []
        if self.conn and subnet_id and vpc_reservations:
            for reservation in vpc_reservations:
                for instance in reservation.instances:
                    if instance.subnet_id == subnet_id:
                        instances.append(dict(
                            id=instance.id,
                            name=TaggedItemView.get_display_name(instance),
                        ))
        return instances

    def get_subnet_network_acls(self, subnet_id=None, vpc_network_acls=None):
        subnet_network_acls = []
        if self.vpc_conn and subnet_id and vpc_network_acls:
            for network_acl in vpc_network_acls:
                subnet_associations = [association.subnet_id for association in network_acl.associations]
                if subnet_id in subnet_associations:
                    subnet_network_acls.append(dict(
                        id=network_acl.id,
                        name=TaggedItemView.get_display_name(network_acl),
                    ))
        return subnet_network_acls

    def get_subnet_route_tables(self, subnet_id=None, vpc_route_tables=None):
        subnet_route_tables = []
        if self.vpc_conn and subnet_id and vpc_route_tables:
            for route_table in vpc_route_tables:
                association_subnet_ids = [assoc.subnet_id for assoc in route_table.associations]
                if subnet_id in association_subnet_ids:
                    subnet_route_tables.append(dict(
                        id=route_table.id,
                        name=TaggedItemView.get_display_name(route_table),
                    ))
                elif association_subnet_ids == [None]:
                    # Show VPC's main route table for subnet
                    subnet_route_tables.append(dict(
                        id=self.vpc_main_route_table.id,
                        name=TaggedItemView.get_display_name(self.vpc_main_route_table),
                    ))
        return subnet_route_tables

    def get_default_security_group(self):
        """Fetch default security group for VPC"""
        filters = {
            'vpc-id': [self.vpc.id],
            'group-name': 'default'
        }
        vpc_security_groups = self.conn.get_all_security_groups(filters=filters)
        if vpc_security_groups:
            return vpc_security_groups[0]
        return None

    def get_main_route_table(self):
        """Fetch main route table for VPC. Returns None if lookup fails"""
        filters = {
            'vpc-id': [self.vpc.id],
            'association.main': 'true'
        }
        route_tables = self.vpc_conn.get_all_route_tables(filters=filters)
        if route_tables:
            return route_tables[0]
        return None

    def get_internet_gateway(self):
        """Fetch internet gateway for VPC. Returns None if lookup fails"""
        filters = {
            'attachment.vpc-id': [self.vpc.id]
        }
        internet_gateways = self.vpc_conn.get_all_internet_gateways(filters=filters)
        if internet_gateways:
            return internet_gateways[0]
        return None

    def update_internet_gateway(self):
        selected_igw = self.request.params.get('internet_gateway')
        actions = []

        if self.vpc_internet_gateway:
            if self.vpc_internet_gateway.id != selected_igw:
                if selected_igw == 'None':
                    actions.append('detach')
                else:
                    actions.append('detach')
                    actions.append('attach')
        elif selected_igw != 'None':
            actions.append('attach')

        actions = set(actions)
        if 'detach' in actions:
            self.vpc_conn.detach_internet_gateway(self.vpc_internet_gateway.id, self.vpc.id)
        if 'attach' in actions:
            self.vpc_conn.attach_internet_gateway(selected_igw, self.vpc.id)


class CreateVPCView(BaseView):
    """Create VPC view and handler"""
    TEMPLATE = '../templates/vpcs/vpc_new.pt'

    def __init__(self, request):
        super(CreateVPCView, self).__init__(request)
        self.title_parts = [_(u'VPC'), _(u'Create')]
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.create_vpc_form = CreateVPCForm(self.request, vpc_conn=self.vpc_conn, formdata=self.request.params or None)
        self.render_dict = dict(
            create_vpc_form=self.create_vpc_form
        )

    @view_config(route_name='vpc_new', renderer=TEMPLATE, request_method='GET')
    def vpc_new(self):
        """Displays the Create VPC page"""
        return self.render_dict

    @view_config(route_name='vpc_create', renderer=TEMPLATE, request_method='POST')
    def vpc_create(self):
        """Handle VPC creation"""
        if self.create_vpc_form.validate():
            name = self.request.params.get('name')
            cidr_block = self.request.params.get('cidr_block')
            internet_gateway = self.request.params.get('internet_gateway')
            tags_json = self.request.params.get('tags')
            self.log_request(_(u"Creating VPC {0}").format(name))
            with boto_error_handler(self.request):
                new_vpc = self.vpc_conn.create_vpc(cidr_block)
                new_vpc_id = new_vpc.id
                self.log_request(_(u"Created VPC {0} ({1})").format(name, new_vpc_id))

                # Add tags
                if name:
                    new_vpc.add_tag('Name', name)
                if tags_json:
                    tags = json.loads(tags_json)
                    tags_dict = TaggedItemView.normalize_tags(tags)
                    for tagname, tagvalue in tags_dict.items():
                        new_vpc.add_tag(tagname, tagvalue)

                # Attach internet gateway to VPC if selected
                if internet_gateway not in [None, 'None']:
                    self.log_request(_(u"Attaching internet gateway to VPC {0}").format(new_vpc_id))
                    self.vpc_conn.attach_internet_gateway(internet_gateway, new_vpc_id)
            msg = _(u'Successfully sent create VPC request. '
                    u'It may take a moment for the VPC to be available.')
            queue = Notification.SUCCESS
            self.request.session.flash(msg, queue=queue)
            location = self.request.route_path('vpc_view', id=new_vpc_id)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_vpc_form.get_errors_list()
        return self.render_dict
