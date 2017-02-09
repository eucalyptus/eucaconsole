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
from operator import attrgetter, itemgetter

import simplejson as json

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config

from ..forms import ChoicesManager
from ..forms.instances import TerminateInstanceForm
from ..forms.vpcs import (
    VPCsFiltersForm, VPCForm, VPCMainRouteTableForm, CreateInternetGatewayForm, CreateVPCForm, CreateSubnetForm,
    RouteTableForm, VPCDeleteForm, SubnetForm, SubnetDeleteForm, RouteTableSetMainForm, RouteTableDeleteForm,
    InternetGatewayForm, InternetGatewayDeleteForm, InternetGatewayDetachForm, CreateRouteTableForm,
    CreateNatGatewayForm, NatGatewayDeleteForm, INTERNET_GATEWAY_HELP_TEXT
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
        self.conn = self.get_connection()
        self.vpc_conn = self.get_connection(conn_type='vpc')
        with boto_error_handler(request, self.location):
            self.vpc = self.get_vpc()
        if self.vpc is None:
            raise HTTPNotFound()
        with boto_error_handler(request, self.location):
            self.vpc_route_tables = self.vpc_conn.get_all_route_tables(filters={'vpc-id': self.vpc.id})
            self.vpc_main_route_table = self.get_main_route_table(route_tables=self.vpc_route_tables)
            self.vpc_internet_gateway = self.get_internet_gateway()
            self.vpc_security_groups = self.conn.get_all_security_groups(filters={'vpc-id': self.vpc.id})
            self.vpc_network_acls = self.vpc_conn.get_all_network_acls(filters={'vpc-id': self.vpc.id})
            self.vpc_default_security_group = self.get_default_security_group(security_groups=self.vpc_security_groups)
            self.suggested_subnet_cidr_block = self.get_suggested_subnet_cidr_block(self.vpc.cidr_block)
            self.vpc_form = VPCForm(
                self.request, vpc=self.vpc, vpc_conn=self.vpc_conn,
                vpc_internet_gateway=self.vpc_internet_gateway, formdata=self.request.params or None)
            self.vpc_main_route_table_form = VPCMainRouteTableForm(
                self.request, vpc=self.vpc, vpc_conn=self.vpc_conn, route_tables=self.vpc_route_tables,
                vpc_main_route_table=self.vpc_main_route_table, formdata=self.request.params or None)
            self.create_internet_gateway_form = CreateInternetGatewayForm(
                self.request, formdata=self.request.params or None)
            self.add_subnet_form = CreateSubnetForm(
                self.request, ec2_conn=self.conn, suggested_subnet_cidr_block=self.suggested_subnet_cidr_block,
                formdata=self.request.params or None
            )
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
            add_subnet_form=self.add_subnet_form,
            create_internet_gateway_form=self.create_internet_gateway_form,
            internet_gateway_help_text=INTERNET_GATEWAY_HELP_TEXT,
            max_subnet_instance_count=10,  # Determines when to link to instances landing page in VPC subnets table
            vpc_default_security_group=self.vpc_default_security_group,
            vpc_security_groups=self.vpc_security_groups,
            vpc_route_tables=self.vpc_route_tables,
            vpc_network_acls=self.vpc_network_acls,
            vpc_main_route_table=self.vpc_main_route_table,
            vpc_main_route_table_name=TaggedItemView.get_display_name(
                self.vpc_main_route_table) if self.vpc_main_route_table else '',
            vpc_internet_gateway=self.vpc_internet_gateway,
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
            deleted_vpc_name = TaggedItemView.get_display_name(self.vpc)
            with boto_error_handler(self.request, self.location):
                # Detach IGW if present
                if self.vpc_internet_gateway:
                    igw_id = self.vpc_internet_gateway.id
                    self.log_request(_('Detaching internet gateway {0} from VPC {1}').format(igw_id, self.vpc.id))
                    self.vpc_conn.detach_internet_gateway(igw_id, self.vpc.id)
                # Delete VPC route tables
                for route_table in self.vpc_route_tables:
                    if route_table != self.vpc_main_route_table:  # Don't explicitly delete main route table
                        self.log_request(_('Deleting route table {0}').format(route_table.id))
                        self.vpc_conn.delete_route_table(route_table.id)
                # Delete VPC security groups
                for security_group in self.vpc_security_groups:
                    if security_group.name != 'default':  # Don't explicitly delete default security group
                        self.log_request(_('Deleting VPC security group {0}').format(security_group.id))
                        security_group.delete()
                # Delete VPC network ACLs
                for network_acl in self.vpc_network_acls:
                    if network_acl.default != 'true':  # Don't explicitly delete default network ACL
                        self.log_request(_('Deleting network ACL {0}').format(network_acl.id))
                        self.vpc_conn.delete_network_acl(network_acl.id)
                # Finally, delete VPC
                self.log_request(_('Deleting VPC {0}').format(self.vpc.id))
                self.vpc_conn.delete_vpc(self.vpc.id)
            msg = _('Successfully deleted VPC {0}').format(deleted_vpc_name)
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.request.route_path('vpcs'))
        else:
            self.request.error_messages = self.vpc_delete_form.get_errors_list()
            return self.render_dict

    @view_config(route_name='vpc_add_subnet', renderer=VIEW_TEMPLATE, request_method='POST')
    def vpc_add_subnet(self):
        location = self.request.route_path('vpc_view', id=self.vpc.id)
        if self.add_subnet_form.validate():
            name = self.request.params.get('subnet_name')
            cidr_block = self.request.params.get('subnet_cidr_block')
            zone = self.request.params.get('availability_zone')
            with boto_error_handler(self.request, location=location):
                self.log_request(_('Adding subnet to VPC {0}').format(self.vpc.id))
                new_subnet = self.vpc_conn.create_subnet(self.vpc.id, cidr_block, availability_zone=zone)
                if name:
                    new_subnet.add_tag('Name', name)
            prefix = _(u'Successfully created subnet')
            msg = '{0} {1}'.format(prefix, new_subnet.id)
            self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            self.request.error_messages = ', '.join(self.add_subnet_form.get_errors_list())
        return HTTPFound(location=location)

    @view_config(route_name='vpc_set_main_route_table', renderer=VIEW_TEMPLATE, request_method='POST')
    def vpc_set_main_route_table(self):
        if self.vpc and self.vpc_main_route_table_form.validate():
            selected_route_table_id = self.request.params.get('route_table')
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

    @view_config(route_name='vpc_create_internet_gateway', renderer=VIEW_TEMPLATE, request_method='POST')
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
            vpcs_list = self.vpc_conn.get_all_vpcs(filters={'vpc_id': vpc_id})
            return vpcs_list[0] if vpcs_list else None
        return None

    def get_vpc_security_groups(self):
        vpc_id = self.request.matchdict.get('id')
        if vpc_id:
            return self.conn.get_all_security_groups(filters={'vpc-id': vpc_id})
        return []

    def get_vpc_subnets(self):
        subnets_list = []
        vpc_id_filter = {'vpc-id': [self.vpc.id]}
        vpc_subnets = self.vpc_conn.get_all_subnets(filters=vpc_id_filter)
        vpc_route_tables = self.vpc_conn.get_all_route_tables(filters=vpc_id_filter)
        vpc_network_acls = self.vpc_network_acls or self.vpc_conn.get_all_network_acls(filters=vpc_id_filter)
        vpc_reservations = self.conn.get_all_reservations(filters=vpc_id_filter)
        for subnet in vpc_subnets:
            instances = self.get_subnet_instances(subnet.id, vpc_reservations)
            subnets_list.append(dict(
                id=subnet.id,
                name=TaggedItemView.get_display_name(subnet),
                state=subnet.state,
                cidr_block=subnet.cidr_block,
                zone=subnet.availability_zone,
                available_ips=subnet.available_ip_address_count,
                instances=instances,
                instance_count=len(instances),
                route_table=self.get_subnet_route_table(subnet.id, vpc_route_tables),
                network_acls=self.get_subnet_network_acls(subnet.id, vpc_network_acls),
            ))
        return subnets_list

    @staticmethod
    def get_subnet_instances(subnet_id, vpc_reservations):
        instances = []
        for reservation in vpc_reservations:
            for instance in reservation.instances:
                if instance.subnet_id == subnet_id:
                    instances.append(dict(
                        id=instance.id,
                        name=TaggedItemView.get_display_name(instance),
                    ))
        return instances

    @staticmethod
    def get_subnet_network_acls(subnet_id, vpc_network_acls):
        subnet_network_acls = []
        for network_acl in vpc_network_acls:
            subnet_associations = [association.subnet_id for association in network_acl.associations]
            if subnet_id in subnet_associations:
                subnet_network_acls.append(dict(
                    id=network_acl.id,
                    name=TaggedItemView.get_display_name(network_acl),
                ))
        return subnet_network_acls

    @staticmethod
    def get_suggested_subnet_cidr_block(vpc_cidr_block):
        """Suggest a subnet CIDR block based on the VPC's CIDR block"""
        vpc_cidr_split = vpc_cidr_block.split('/')
        cidr_ip = vpc_cidr_split[0]
        cidr_netmask = int(vpc_cidr_split[1])
        cidr_ip_parts = cidr_ip.split('.')
        num_ip_parts = 2
        ip_suffix = '.128.0'  # The 128 in '.128.0' is somewhat arbitrary but seems safer than suggesting '.0.0'

        if 16 <= cidr_netmask < 24:
            pass  # Use above defaults for num_ip_parts and ip_suffix

        if cidr_netmask >= 24:
            num_ip_parts = 3
            ip_suffix = '.128'

        # Suggest a subnet netmask __ bits offset from the VPC netmask
        if 16 <= cidr_netmask <= 24:
            netmask_bits_offset = 4
        elif 24 < cidr_netmask <= 26:
            netmask_bits_offset = 2
        else:
            # Although a VPC is unlikely to have a /27 or /28 netmask, we still need a fallback value
            netmask_bits_offset = 0

        subnet_netmask = cidr_netmask + netmask_bits_offset

        return '{0}{1}/{2}'.format('.'.join(cidr_ip_parts[:num_ip_parts]), ip_suffix, subnet_netmask)

    def get_subnet_route_table(self, subnet_id, vpc_route_tables):
        for route_table in vpc_route_tables:
            association_subnet_ids = [assoc.subnet_id for assoc in route_table.associations]
            if subnet_id in association_subnet_ids:
                return route_table
            elif association_subnet_ids == [None]:
                return self.vpc_main_route_table

    @staticmethod
    def get_default_security_group(security_groups):
        """Fetch default security group for VPC"""
        security_groups_named_default = [sgroup for sgroup in security_groups if sgroup.name == 'default']
        if security_groups_named_default:
            return security_groups_named_default[0]
        return None

    @staticmethod
    def get_main_route_table(route_tables):
        """Fetch main route table for VPC. Returns None if lookup fails"""
        for route_table in route_tables:
            if [association for association in route_table.associations if association.main is True]:
                return route_table
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
            msg = _(u'Successfully created VPC. '
                    u'It may take a moment for the VPC to be available.')
            queue = Notification.SUCCESS
            self.request.session.flash(msg, queue=queue)
            location = self.request.route_path('vpc_view', id=new_vpc_id)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_vpc_form.get_errors_list()
        return self.render_dict


class RouteTableMixin(object):
    def update_routes(self, request, vpc_conn, route_table):
        routes_json = request.params.get('routes')
        new_routes = json.loads(routes_json)
        self.delete_routes(vpc_conn, route_table)
        self.add_routes(vpc_conn, route_table, new_routes)

    @staticmethod
    def delete_routes(vpc_conn, route_table):
        for route in route_table.routes:
            # Skip deleting local route
            if route.gateway_id != 'local':
                vpc_conn.delete_route(route_table.id, route.destination_cidr_block)

    @staticmethod
    def add_routes(vpc_conn, route_table, new_routes):
        for route in new_routes:
            route_target_id = route.get('target')
            params = dict(
                route_table_id=route_table.id,
                destination_cidr_block=route.get('destination_cidr_block')
            )
            if route_target_id:
                if route_target_id.startswith('igw-'):
                    params.update(dict(gateway_id=route_target_id))
                elif route_target_id.startswith('eni-'):
                    params.update(dict(interface_id=route_target_id))
                # TODO: Handle routes with NAT Gateway target
                vpc_conn.create_route(**params)


class SubnetView(TaggedItemView, RouteTableMixin):
    VIEW_TEMPLATE = '../templates/vpcs/subnet_view.pt'

    def __init__(self, request, **kwargs):
        super(SubnetView, self).__init__(request, **kwargs)
        self.location = self.request.route_path(
            'subnet_view', vpc_id=self.request.matchdict.get('vpc_id'), id=self.request.matchdict.get('id'))
        self.conn = self.get_connection()
        self.conn3 = self.get_connection3()
        self.vpc_conn = self.get_connection(conn_type='vpc')
        with boto_error_handler(request, self.location):
            self.vpc = self.get_vpc()
            self.subnet = self.get_subnet()
        if self.subnet is None or self.vpc is None:
            raise HTTPNotFound()
        with boto_error_handler(request, self.location):
            self.vpc_route_tables = self.vpc_conn.get_all_route_tables(filters={'vpc-id': self.vpc.id})
            self.subnet_route_table = self.get_subnet_route_table()
            self.subnet_network_acl = self.get_subnet_network_acl()
            self.create_nat_gateway_form = CreateNatGatewayForm(
                self.request, ec2_conn=self.conn, formdata=self.request.params or None)
            self.subnet_form = SubnetForm(
                self.request, vpc_conn=self.vpc_conn, vpc=self.vpc, route_tables=self.vpc_route_tables,
                subnet=self.subnet, subnet_route_table=self.subnet_route_table, formdata=self.request.params or None
            )
        self.create_route_table_form = CreateRouteTableForm(self.request, formdata=self.request.params or None)
        self.subnet_delete_form = SubnetDeleteForm(self.request, formdata=self.request.params or None)
        self.terminate_form = TerminateInstanceForm(self.request, formdata=self.request.params or None)
        self.vpc_name = self.get_display_name(self.vpc)
        self.subnet_name = self.get_display_name(self.subnet)
        self.tagged_obj = self.subnet
        self.title_parts = [_(u'Subnet'), self.subnet_name]
        subnet_is_default_for_zone = self.subnet.defaultForAz == 'true'
        vpc_local_route = dict(destination_cidr_block=self.vpc.cidr_block, state='active', gateway_id='local')
        self.render_dict = dict(
            vpc=self.vpc,
            vpc_name=self.vpc_name,
            subnet=self.subnet,
            subnet_name=self.subnet_name,
            subnet_route_table=self.subnet_route_table,
            subnet_network_acl=self.subnet_network_acl,
            subnet_nat_gateways=self.get_subnet_nat_gateways(),
            subnet_form=self.subnet_form,
            subnet_delete_form=self.subnet_delete_form,
            routes=json.dumps([vpc_local_route]),
            create_route_table_form=self.create_route_table_form,
            create_nat_gateway_form=self.create_nat_gateway_form,
            terminate_form=self.terminate_form,
            subnet_instances_link=self.request.route_path('instances', _query={'subnet_id': self.subnet.id}),
            default_for_zone=subnet_is_default_for_zone,
            default_for_zone_label=_('yes') if subnet_is_default_for_zone else _('no'),
            public_ip_auto_assignment=_('Enabled') if self.subnet.mapPublicIpOnLaunch == 'true' else _('Disabled'),
            tags=self.serialize_tags(self.subnet.tags) if self.subnet else [],
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='subnet_view', renderer=VIEW_TEMPLATE, request_method='GET')
    def subnet_view(self):
        if self.subnet is None:
            raise HTTPNotFound()
        return self.render_dict

    @view_config(route_name='subnet_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def subnet_update(self):
        if self.subnet and self.subnet_form.validate():
            location = self.request.route_path('subnet_view', vpc_id=self.vpc.id, id=self.subnet.id)
            with boto_error_handler(self.request, location):
                # Update tags
                self.update_tags()

                # Save Name tag
                name = self.request.params.get('name', '')
                self.update_name_tag(name)

                # Update route table
                self.update_route_table()

                # Update public IP auto-assignment value
                self.modify_public_auto_ip_assignment()

            msg = _(u'Successfully updated subnet')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.subnet_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='subnet_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def subnet_delete(self):
        if self.subnet and self.subnet_delete_form.validate():
            deleted_subnet_name = TaggedItemView.get_display_name(self.subnet)
            with boto_error_handler(self.request, self.location):
                # Disassociate route table from subnet
                if self.subnet_route_table:
                    for association in self.subnet_route_table.associations:
                        if association.subnet_id == self.subnet.id:
                            self.vpc_conn.disassociate_route_table(association.id)

                # Disassociate network ACL from subnet
                if self.subnet_network_acl:
                    self.vpc_conn.disassociate_network_acl(self.subnet.id)

                # Finally, delete subnet
                self.log_request(_('Deleting subnet {0}').format(self.subnet.id))
                self.vpc_conn.delete_subnet(self.subnet.id)

            msg = _('Successfully deleted subnet {0}').format(deleted_subnet_name)
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.request.route_path('vpc_view', id=self.vpc.id))
        else:
            self.request.error_messages = self.subnet_delete_form.get_errors_list()
            return self.render_dict

    @view_config(route_name='route_table_create', renderer=VIEW_TEMPLATE, request_method='POST')
    def route_table_create(self):
        location = self.request.route_path('subnet_view', vpc_id=self.vpc.id, id=self.subnet.id)
        if self.create_route_table_form.validate():
            with boto_error_handler(self.request, location):
                name = self.request.params.get('route_table_name')
                with boto_error_handler(self.request):
                    self.log_request('Creating route table in VPC {0}'.format(self.vpc.id))
                    new_route_table = self.vpc_conn.create_route_table(self.vpc.id)
                    routes_json = self.request.params.get('routes')
                    new_routes = json.loads(routes_json)
                    # Skip 'local' route, which is added automatically
                    new_routes = [route for route in new_routes if route.get('gateway_id') != 'local']
                    self.add_routes(self.vpc_conn, new_route_table, new_routes)
                    if name:
                        new_route_table.add_tag('Name', name)
                msg = _(u'Successfully created route table {0}'.format(new_route_table.id))
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            self.request.error_messages = ', '.join(self.create_route_table_form.get_errors_list())
        return HTTPFound(location=location)

    @view_config(route_name='nat_gateway_create', renderer=VIEW_TEMPLATE, request_method='POST')
    def nat_gateway_create(self):
        location = self.request.route_path('subnet_view', vpc_id=self.vpc.id, id=self.subnet.id)
        if self.create_nat_gateway_form.validate():
            with boto_error_handler(self.request, location):
                subnet_id = self.request.params.get('nat_gateway_subnet_id')
                eip_allocation_id = self.request.params.get('eip_allocation_id')
                with boto_error_handler(self.request):
                    self.log_request('Creating NAT gateway in VPC {0}'.format(self.vpc.id))
                    # Leverage botocore to create NAT gateway
                    self.conn3.create_nat_gateway(SubnetId=subnet_id, AllocationId=eip_allocation_id)
                msg = _(u'Successfully created NAT gateway {0}'.format(self.subnet.id))
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            self.request.error_messages = ', '.join(self.create_nat_gateway_form.get_errors_list())
        return HTTPFound(location=location)

    def get_vpc(self):
        vpc_id = self.request.matchdict.get('vpc_id')
        if vpc_id:
            vpcs_list = self.vpc_conn.get_all_vpcs(filters={'vpc_id': vpc_id})
            return vpcs_list[0] if vpcs_list else None
        return None

    def get_subnet(self):
        subnet_id = self.request.matchdict.get('id')
        if subnet_id:
            subnet_list = self.vpc_conn.get_all_subnets(filters={'subnet-id': [subnet_id]})
            return subnet_list[0] if subnet_list else None
        return None

    def get_subnet_route_table(self):
        for route_table in self.vpc_route_tables:
            if [association for association in route_table.associations if association.subnet_id == self.subnet.id]:
                return route_table
        return None

    def get_subnet_network_acl(self):
        vpc_network_acls = self.vpc_conn.get_all_network_acls(filters={'vpc-id': self.vpc.id})
        subnet_network_acls = VPCView.get_subnet_network_acls(self.subnet.id, vpc_network_acls)
        if subnet_network_acls:
            return subnet_network_acls[0]
        return None

    def get_subnet_nat_gateways(self):
        filters = [{'Name': 'subnet-id', 'Values': [self.subnet.id]}]
        subnet_nat_gateways_resp = self.conn3.describe_nat_gateways(Filters=filters)
        nat_gateways = subnet_nat_gateways_resp.get('NatGateways')
        return reversed(sorted(nat_gateways, key=itemgetter('CreateTime')))

    def update_route_table(self):
        new_route_table_id = self.request.params.get('route_table')
        actions = []
        if self.subnet_route_table and new_route_table_id == 'None':
            actions.append('disassociate')
        if not self.subnet_route_table and new_route_table_id != 'None':
            actions.append('associate')
        if self.subnet_route_table and new_route_table_id != 'None':
            actions.append('disassociate')
            actions.append('associate')
        if 'disassociate' in actions:
            for association in self.subnet_route_table.associations:
                if association.subnet_id == self.subnet.id:
                    self.vpc_conn.disassociate_route_table(association.id)
        if 'associate' in actions:
            self.vpc_conn.associate_route_table(new_route_table_id, self.subnet.id)

    def modify_public_auto_ip_assignment(self):
        map_public_ip_on_launch = self.request.params.get('public_ip_auto_assignment', 'false')
        params = {
            'SubnetId': self.subnet.id,
            'MapPublicIpOnLaunch.Value': map_public_ip_on_launch
        }
        self.vpc_conn.get_status('ModifySubnetAttribute', params)

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'subnet_id': self.subnet.id,
            'terminated_instances_notice': _(
                'Successfully sent request to terminate instances. It may take a moment to shut down the instances.'
            ),
        }))


class RouteTableView(TaggedItemView, RouteTableMixin):
    VIEW_TEMPLATE = '../templates/vpcs/route_table_view.pt'

    def __init__(self, request, **kwargs):
        super(RouteTableView, self).__init__(request, **kwargs)
        self.location = self.request.route_path(
            'route_table_view', vpc_id=self.request.matchdict.get('vpc_id'), id=self.request.matchdict.get('id'))
        self.conn = self.get_connection()  # Required for tag updates
        self.vpc_conn = self.get_connection(conn_type='vpc')
        with boto_error_handler(request, self.location):
            self.vpc = self.get_vpc()
            self.route_table = self.get_route_table(self.vpc.id)
        if self.route_table is None or self.vpc is None:
            raise HTTPNotFound()
        with boto_error_handler(request, self.location):
            self.route_table_subnets = self.get_route_table_subnets()
            vpc_main_route_tables = self.vpc_conn.get_all_route_tables(
                filters={'vpc-id': self.vpc.id, 'association.main': 'true'})
        self.vpc_main_route_table = vpc_main_route_tables[0]
        self.route_table_name = self.get_display_name(self.route_table)
        self.is_main_route_table = self.route_table.id == self.vpc_main_route_table.id
        self.route_table_form = RouteTableForm(
            self.request, route_table=self.route_table, formdata=self.request.params or None
        )
        self.route_table_delete_form = RouteTableDeleteForm(self.request, formdata=self.request.params or None)
        self.route_table_set_main_form = RouteTableSetMainForm(self.request, formdata=self.request.params or None)
        self.vpc_name = self.get_display_name(self.vpc)
        self.tagged_obj = self.route_table
        self.title_parts = [_(u'Route Table'), self.route_table_name]
        self.render_dict = dict(
            vpc=self.vpc,
            vpc_name=self.vpc_name,
            route_table=self.route_table,
            route_table_name=self.route_table_name,
            route_table_subnets=self.route_table_subnets,
            is_main_route_table=self.is_main_route_table,
            main_route_table_label=_('yes') if self.is_main_route_table else _('no'),
            route_table_form=self.route_table_form,
            route_table_delete_form=self.route_table_delete_form,
            route_table_set_main_form=self.route_table_set_main_form,
            routes=self.serialize_routes(self.route_table.routes),
            tags=self.serialize_tags(self.route_table.tags) if self.route_table else [],
        )

    @view_config(route_name='route_table_view', renderer=VIEW_TEMPLATE, request_method='GET')
    def route_table_view(self):
        if self.route_table is None:
            raise HTTPNotFound()
        return self.render_dict

    @view_config(route_name='route_table_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def route_table_update(self):
        if self.route_table and self.route_table_form.validate():
            location = self.request.route_path('route_table_view', vpc_id=self.vpc.id, id=self.route_table.id)
            routes_updated = self.request.params.get('routes_updated', False)
            with boto_error_handler(self.request, location):
                # Update tags
                self.update_tags()

                # Save Name tag
                name = self.request.params.get('name', '')
                self.update_name_tag(name)

                # Update routes
                if routes_updated:
                    self.update_routes(self.request, self.vpc_conn, self.route_table)

            msg = _(u'Successfully updated route table')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.route_table_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='route_table_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def route_table_delete(self):
        if self.route_table and self.route_table_delete_form.validate():
            with boto_error_handler(self.request, self.location):
                # Disassociate any subnets from route table
                for association in self.route_table.associations:
                    self.vpc_conn.disassociate_route_table(association.id)

                # Delete route table
                self.vpc_conn.delete_route_table(self.route_table.id)

            msg = _(u'Successfully deleted route table')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.request.route_path('vpcs'))
        else:
            self.request.error_messages = self.route_table_delete_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='route_table_set_main_for_vpc', renderer=VIEW_TEMPLATE, request_method='POST')
    def route_table_set_main_for_vpc(self):
        if self.vpc and self.route_table_set_main_form.validate():
            if self.vpc_main_route_table:
                existing_main_table_associations = [
                    assoc for assoc in self.vpc_main_route_table.associations if assoc.main is True]
                if existing_main_table_associations:
                    existing_assocation_id = existing_main_table_associations[0].id
                    with boto_error_handler(self.request, self.location):
                        self.vpc_conn.replace_route_table_association_with_assoc(
                            association_id=existing_assocation_id, route_table_id=self.route_table.id)
            msg = _(u'Successfully set main route table for VPC')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.location)
        else:
            self.request.error_messages = self.route_table_set_main_form.get_errors_list()
        return self.render_dict

    def get_vpc(self):
        vpc_id = self.request.matchdict.get('vpc_id')
        if vpc_id:
            vpcs_list = self.vpc_conn.get_all_vpcs(filters={'vpc_id': vpc_id})
            return vpcs_list[0] if vpcs_list else None
        return None

    def get_route_table(self, vpc_id):
        route_table_id = self.request.matchdict.get('id')
        filters = {
            'vpc-id': vpc_id,
            'route-table-id': route_table_id
        }
        route_tables = self.vpc_conn.get_all_route_tables(filters=filters)
        if route_tables:
            return route_tables[0]
        return None

    def get_route_table_subnets(self):
        route_table_association_subnet_ids = [assoc.subnet_id for assoc in self.route_table.associations]
        return self.vpc_conn.get_all_subnets(filters={'subnet-id': route_table_association_subnet_ids})

    @staticmethod
    def serialize_routes(routes):
        """Returns a JSON-stringified list of boto.vpc.RouteTable.Route objects converted to dicts"""
        routes_list = []
        for route in routes:
            routes_list.append(dict(
                destination_cidr_block=route.destination_cidr_block,
                gateway_id=route.gateway_id,
                instance_id=route.instance_id,
                interface_id=route.interface_id,
                origin=route.origin,
                state=route.state,
                vpc_peering_connection_id=route.vpc_peering_connection_id,
            ))
        return BaseView.escape_json(json.dumps(routes_list))


class RouteTargetsJsonView(BaseView):
    """Route targets returned as JSON"""

    def __init__(self, request):
        super(RouteTargetsJsonView, self).__init__(request)
        self.vpc_conn = self.get_connection(conn_type="vpc")

    @view_config(route_name='route_targets_json', renderer='json', request_method='GET')
    def route_targets_json(self):
        route_targets = []
        vpc_id = self.request.matchdict.get('vpc_id')
        with boto_error_handler(self.request):
            internet_gateways = self.vpc_conn.get_all_internet_gateways(filters={'attachment.vpc-id': [vpc_id]})
            network_interfaces = self.vpc_conn.get_all_network_interfaces(filters={'vpc-id': [vpc_id]})
            # TODO: Add NAT gateways as target options
        for igw in sorted(internet_gateways, key=attrgetter('id')):
            route_targets.append(dict(
                id=igw.id,
            ))
        for eni in sorted(network_interfaces, key=attrgetter('id')):
            route_targets.append(dict(
                id=eni.id
            ))
        return dict(results=route_targets)


class InternetGatewayView(TaggedItemView):
    VIEW_TEMPLATE = '../templates/vpcs/internet_gateway_view.pt'

    def __init__(self, request, **kwargs):
        super(InternetGatewayView, self).__init__(request, **kwargs)
        self.location = self.request.route_path('internet_gateway_view', id=self.request.matchdict.get('id'))
        self.conn = self.get_connection()  # Required for tag updates
        self.vpc_conn = self.get_connection(conn_type='vpc')
        with boto_error_handler(request, self.location):
            self.internet_gateway = self.get_internet_gateway()
        if self.internet_gateway is None:
            raise HTTPNotFound()
        with boto_error_handler(request, self.location):
            self.internet_gateway_vpc = self.get_internet_gateway_vpc()
        self.internet_gateway_form = InternetGatewayForm(
            self.request, internet_gateway=self.internet_gateway, formdata=self.request.params or None
        )
        self.internet_gateway_delete_form = InternetGatewayDeleteForm(
            self.request, formdata=self.request.params or None)
        self.internet_gateway_detach_form = InternetGatewayDetachForm(
            self.request, formdata=self.request.params or None)
        self.internet_gateway_name = self.get_display_name(self.internet_gateway)
        self.tagged_obj = self.internet_gateway
        self.title_parts = [_('Internet Gateway'), self.internet_gateway_name]
        self.is_attached = len(self.internet_gateway.attachments) > 0
        self.render_dict = dict(
            internet_gateway=self.internet_gateway,
            internet_gateway_name=self.internet_gateway_name,
            internet_gateway_form=self.internet_gateway_form,
            internet_gateway_detach_form=self.internet_gateway_detach_form,
            internet_gateway_delete_form=self.internet_gateway_delete_form,
            internet_gateway_vpc=self.internet_gateway_vpc,
            is_attached=self.is_attached,
            igw_status=_('attached') if self.is_attached else _('available'),
            tags=self.serialize_tags(self.internet_gateway.tags) if self.internet_gateway else [],
        )

    @view_config(route_name='internet_gateway_view', renderer=VIEW_TEMPLATE, request_method='GET')
    def internet_gateway_view(self):
        return self.render_dict

    @view_config(route_name='internet_gateway_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def internet_gateway_update(self):
        if self.internet_gateway and self.internet_gateway_form.validate():
            location = self.request.route_path('internet_gateway_view', id=self.internet_gateway.id)
            with boto_error_handler(self.request, location):
                # Update tags
                self.update_tags()

                # Save Name tag
                name = self.request.params.get('name', '')
                self.update_name_tag(name)

            msg = _(u'Successfully updated internet gateway')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.internet_gateway_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='internet_gateway_detach', renderer=VIEW_TEMPLATE, request_method='POST')
    def internet_gateway_detach(self):
        if self.internet_gateway and self.internet_gateway_detach_form.validate():
            location = self.request.route_path('internet_gateway_view', id=self.internet_gateway.id)
            with boto_error_handler(self.request, location):
                log_msg = _('Detaching internet gateway {0} from VPC {1}').format(
                    self.internet_gateway.id, self.internet_gateway_vpc.id)
                self.log_request(log_msg)
                self.vpc_conn.detach_internet_gateway(self.internet_gateway.id, self.internet_gateway_vpc.id)

            msg = _(u'Successfully detached internet gateway from VPC')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.internet_gateway_detach_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='internet_gateway_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def internet_gateway_delete(self):
        if self.internet_gateway and self.internet_gateway_delete_form.validate():
            location = self.request.route_path('internet_gateway_view', id=self.internet_gateway.id)
            with boto_error_handler(self.request, location):
                log_msg = _('Deleting internet gateway {0}').format(self.internet_gateway.id)
                self.log_request(log_msg)
                self.vpc_conn.delete_internet_gateway(self.internet_gateway.id)
            msg = _(u'Successfully deleted internet gateway')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.request.route_path('vpcs'))
        else:
            self.request.error_messages = self.internet_gateway_delete_form.get_errors_list()
        return self.render_dict

    def get_internet_gateway(self):
        igw_id = self.request.matchdict.get('id')
        if igw_id:
            igws_list = self.vpc_conn.get_all_internet_gateways(filters={'internet-gateway-id': igw_id})
            return igws_list[0] if igws_list else None
        return None

    def get_internet_gateway_vpc(self):
        if self.internet_gateway.attachments:
            vpc_id = self.internet_gateway.attachments[0].vpc_id
            vpcs_list = self.vpc_conn.get_all_vpcs(filters={'vpc_id': vpc_id})
            if vpcs_list:
                return vpcs_list[0]
        return None


class NatGatewayView(BaseView):
    VIEW_TEMPLATE = '../templates/vpcs/nat_gateway_view.pt'

    def __init__(self, request, **kwargs):
        super(NatGatewayView, self).__init__(request, **kwargs)
        self.vpc_id = self.request.matchdict.get('vpc_id')
        self.nat_gateway_id = self.request.matchdict.get('id')
        self.location = self.request.route_path('nat_gateway_view', vpc_id=self.vpc_id, id=self.nat_gateway_id)
        self.vpc_conn = self.get_connection(conn_type='vpc')
        self.conn3 = self.get_connection3()
        with boto_error_handler(request, self.location):
            self.nat_gateway = self.get_nat_gateway()
            self.nat_gateway_vpc = self.get_nat_gateway_vpc()
        if self.nat_gateway is None or self.nat_gateway_vpc is None:
            raise HTTPNotFound()
        self.subnet_id = self.nat_gateway.get('SubnetId')
        with boto_error_handler(request, self.location):
            self.nat_gateway_subnet = self.get_nat_gateway_subnet()
        self.nat_gateway_delete_form = NatGatewayDeleteForm(self.request, formdata=self.request.params or None)
        self.title_parts = [_('NAT Gateway'), self.nat_gateway_id]
        self.render_dict = dict(
            nat_gateway=self.nat_gateway,
            nat_gateway_id=self.nat_gateway_id,
            nat_gateway_vpc=self.nat_gateway_vpc,
            nat_gateway_subnet=self.nat_gateway_subnet,
            nat_gateway_delete_form=self.nat_gateway_delete_form,
            nat_gateway_network_info=self.get_nat_gateway_network_info(),
        )

    @view_config(route_name='nat_gateway_view', renderer=VIEW_TEMPLATE, request_method='GET')
    def nat_gateway_view(self):
        return self.render_dict

    @view_config(route_name='nat_gateway_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def nat_gateway_delete(self):
        if self.nat_gateway and self.nat_gateway_delete_form.validate():
            location = self.request.route_path('nat_gateway_view', id=self.nat_gateway_id)
            with boto_error_handler(self.request, location):
                log_msg = _('Deleting NAT gateway {0}').format(self.nat_gateway_id)
                self.log_request(log_msg)
                # TODO: Delete NAT gateway
            msg = _(u'Successfully deleted NAT gateway')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=self.request.route_path('vpcs'))
        else:
            self.request.error_messages = self.nat_gateway_delete_form.get_errors_list()
        return self.render_dict

    def get_nat_gateway(self):
        filters = [
            {'Name': 'vpc-id', 'Values': [self.vpc_id]},
            {'Name': 'nat-gateway-id', 'Values': [self.nat_gateway_id]}
        ]
        subnet_nat_gateways_resp = self.conn3.describe_nat_gateways(Filters=filters)
        nat_gateways = subnet_nat_gateways_resp.get('NatGateways')
        return nat_gateways[0] if nat_gateways else None

    def get_nat_gateway_vpc(self):
        vpc_list = self.vpc_conn.get_all_vpcs(filters={'vpc-id': [self.vpc_id]})
        return vpc_list[0] if vpc_list else None

    def get_nat_gateway_subnet(self):
        subnet_list = self.vpc_conn.get_all_subnets(filters={'subnet-id': [self.subnet_id]})
        return subnet_list[0] if subnet_list else None

    def get_nat_gateway_network_info(self):
        addresses = self.nat_gateway.get('NatGatewayAddresses')
        if addresses:
            return addresses[0]
        return {}

