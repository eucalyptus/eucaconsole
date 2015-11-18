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
Pyramid views for Dashboard

"""
import simplejson as json

from pyramid.view import view_config
from boto.exception import BotoServerError

from ..forms import ChoicesManager
from . import BaseView
from ..i18n import _
from . import boto_error_handler
from .. import utils

TILE_MASTER_LIST = [
    ('instances-running', 'Running instances'),
    ('instances-stopped', 'Stopped instances'),
    ('stacks', 'Stacks'),
    ('scaling-groups', 'Instances in scaling groups'),
    ('elastic-ips', 'Elastic IPs'),
    ('security-groups', 'Security groups'),
    ('key-pairs', 'Key pairs'),
    ('load-balancers', 'Load balancers'),
    ('health', 'Service status'),
    ('volumes', 'Volumes'),
    ('snapshots', 'Snapshots'),
    ('buckets', 'Buckets (S3)'),
    ('accounts', 'Accounts'),
    ('users', 'Users'),
    ('groups', 'Groups'),
    ('roles', 'Roles')
]


class DashboardView(BaseView):

    def __init__(self, request):
        super(DashboardView, self).__init__(request)
        self.title_parts = [_(u'Dashboard')]
        self.conn = self.get_connection()

    @view_config(route_name='dashboard', request_method='GET', renderer='../templates/dashboard.pt')
    def dashboard_home(self):
        with boto_error_handler(self.request):
            region = self.request.session.get('region')
            availability_zones = ChoicesManager(self.conn).get_availability_zones(region)
        tiles = self.request.cookies.get(u"{0}_dash_order".format(
            self.request.session['account' if self.cloud_type == 'euca' else 'access_id']))
        if tiles is not None:
            tiles = tiles.replace('%2C', ',')
        else:
            tiles = ','.join([tile for (tile, label) in TILE_MASTER_LIST])

        tiles_not_shown = [tile for (tile, label) in TILE_MASTER_LIST if tile not in tiles.split(',')]
        tiles_default = [tile for (tile, label) in TILE_MASTER_LIST]
        session = self.request.session
        if session['cloud_type'] == 'aws':
            try:
                tiles_not_shown.remove('users')
                tiles_default.remove('users')
            except ValueError:
                pass
            try:
                tiles_not_shown.remove('groups')
                tiles_default.remove('groups')
            except ValueError:
                pass
            try:
                tiles_not_shown.remove('roles')
                tiles_default.remove('roles')
            except ValueError:
                pass
            try:
                tiles_not_shown.remove('accounts')
                tiles_default.remove('accounts')
            except ValueError:
                pass
        else:
            if session['account'] != 'eucalyptus':
                try:
                    tiles_not_shown.remove('accounts')
                    tiles_default.remove('accounts')
                except ValueError:
                    pass

        tiles_are_default = (tiles == ','.join(tiles_default))
        return dict(
            availability_zones=availability_zones,
            tiles=tiles.split(','),
            tiles_not_shown=[(tile, label) for (tile, label) in TILE_MASTER_LIST if tile in tiles_not_shown],
            tiles_are_default=tiles_are_default,
            controller_options_json=self.get_controller_options_json(),
            ufshost_error=utils.is_ufshost_error(self.conn, self.cloud_type)
        )

    def get_controller_options_json(self):
        services = [
            dict(name=_(u'Compute'), status=''),
            dict(name=_(u'Object Storage'), status=''),
            dict(name=_(u'Auto Scaling'), status=''),
            dict(name=_(u'Elastic Load Balancing'), status=''),
            dict(name=_(u'CloudWatch'), status=''),
            dict(name=_(u'CloudFormation'), status=''),
        ]
        session = self.request.session
        if session['cloud_type'] == 'euca':
            services.append(dict(name=_(u'Identity & Access Mgmt'), status=''))
        storage_key = self.get_shared_buckets_storage_key(self.conn.host)
        return BaseView.escape_json(json.dumps({
            'json_items_url': self.request.route_path('dashboard_json'),
            'services': services,
            'service_status_url': self.request.route_path('service_status_json'),
            'cloud_type': self.cloud_type,
            'account_display_name': self.get_account_display_name(),
            'storage_key': storage_key
        }))


class DashboardJsonView(BaseView):
    @view_config(route_name='dashboard_json', request_method='GET', renderer='json')
    def dashboard_json(self):
        ec2_conn = self.get_connection()
        elb_conn = self.get_connection(conn_type='elb')

        # Fetch availability zone if set
        zone = self.request.params.get('zone')
        filters = {}
        if zone:
            filters = {'availability-zone': zone}

        # Instances counts
        instances_total_count = instances_running_count = instances_stopped_count = instances_scaling_count = 0

        # Get list of tiles so we can fetch only data for tiles the user is showing
        tiles = self.request.cookies.get(u"{0}_dash_order".format(
            self.request.session['account' if self.cloud_type == 'euca' else 'access_id']))
        if tiles is None:
            tiles = ','.join([tile for (tile, label) in TILE_MASTER_LIST])
        with boto_error_handler(self.request):
            if ('instances-running' or 'instances-stopped' or 'scaling-groups') in tiles:
                for instance in ec2_conn.get_only_instances(filters=filters):
                    instances_total_count += 1
                    if instance.tags.get('aws:autoscaling:groupName') and instance.state == u'running':
                        instances_scaling_count += 1
                    if instance.state == u'running':
                        instances_running_count += 1
                    elif instance.state == u'stopped':
                        instances_stopped_count += 1

            # Volume/snapshot counts
            volumes_count = len(ec2_conn.get_all_volumes(filters=filters)) if 'volumes' in tiles else 0
            snapshots_count = len(ec2_conn.get_all_snapshots(owner='self')) if 'snapshots' in tiles else 0
            buckets_count = 0
            try:
                s3_conn = self.get_connection(conn_type="s3")
                buckets_count = len(s3_conn.get_all_buckets()) if 'buckets' in tiles else 0
            except BotoServerError:
                pass

            # Security groups, key pairs, IP addresses
            securitygroups_count = len(ec2_conn.get_all_security_groups()) if 'security-groups' in tiles else 0
            keypairs_count = len(ec2_conn.get_all_key_pairs()) if 'key-pairs' in tiles else 0
            elasticips_count = len(ec2_conn.get_all_addresses()) if 'elastic-ips' in tiles else 0
            loadbalancers_count = len(elb_conn.get_all_load_balancers()) if 'load-balancers' in tiles else 0

            # TODO: catch errors in this block and turn iam health off
            # IAM counts
            accounts_count = 0
            users_count = 0
            groups_count = 0
            roles_count = 0
            session = self.request.session
            if session['cloud_type'] == 'euca':
                iam_conn = self.get_connection(conn_type="iam")
                if session['account_access']:
                    accounts_count = len(iam_conn.get_response(
                        'ListAccounts', params={}, list_marker='Accounts').accounts)
                if session['user_access']:
                    users_count = len(iam_conn.get_all_users().users) if 'users' in tiles else 0
                if session['group_access']:
                    groups_count = len(iam_conn.get_all_groups().groups) if 'groups' in tiles else 0
                if session['role_access']:
                    roles_count = len(iam_conn.list_roles().roles) if 'roles' in tiles else 0

            stacks_count = 0
            try:
                cf_conn = self.get_connection(conn_type="cloudformation")
                stacks_count = len(cf_conn.describe_stacks()) if 'stacks' in tiles else 0
            except BotoServerError:
                pass

            return dict(
                instance_total=instances_total_count,
                instances_running=instances_running_count,
                instances_stopped=instances_stopped_count,
                instances_scaling=instances_scaling_count,
                stacks=stacks_count,
                volumes=volumes_count,
                snapshots=snapshots_count,
                buckets=buckets_count,
                securitygroups=securitygroups_count,
                keypairs=keypairs_count,
                loadbalancers=loadbalancers_count,
                eips=elasticips_count,
                accounts=accounts_count,
                users=users_count,
                groups=groups_count,
                roles=roles_count,
                health=dict(name=_(u'Compute'), status='up'),  # this determined client-side
            )

    @view_config(route_name='service_status_json', request_method='GET', renderer='json')
    def service_status_json(self):
        svc = self.request.params.get('svc')
        with boto_error_handler(self.request):
            status = 'up'
            if svc == _(u'Object Storage'):
                conn = self.get_connection(conn_type="s3")
                try:
                    conn.get_all_buckets()
                except BotoServerError as err:
                    if err.message.find('Insufficient permissions') > -1:
                        status = 'denied'
                    else:
                        status = 'down'
            elif svc == _(u'Auto Scaling'):
                conn = self.get_connection(conn_type="autoscale")
                try:
                    conn.get_all_groups(max_records=1)
                except BotoServerError as err:
                    if err.code == 'UnauthorizedOperation':
                        status = 'denied'
                    else:
                        status = 'down'
            elif svc == _(u'Elastic Load Balancing'):
                conn = self.get_connection(conn_type="elb")
                try:
                    conn.get_all_load_balancers()
                except BotoServerError as err:
                    if err.code == 'UnauthorizedOperation':
                        status = 'denied'
                    else:
                        status = 'down'
            elif svc == _(u'CloudWatch'):
                conn = self.get_connection(conn_type="cloudwatch")
                try:
                    conn.list_metrics(namespace="AWS/EC2")
                except BotoServerError as err:
                    if err.code == 'UnauthorizedOperation':
                        status = 'denied'
                    else:
                        status = 'down'
            elif svc == _(u'Identiy & Access Mgmt'):
                conn = self.get_connection(conn_type="iam")
                try:
                    conn.get_all_groups(path_prefix="/notlikely")
                except BotoServerError as err:
                    if err.code == 'UnauthorizedOperation':
                        status = 'denied'
                    else:
                        status = 'down'
            elif svc == _(u'CloudFoundations'):
                conn = self.get_connection(conn_type="cloudfoundation")
                try:
                    # we don't support update, and it's transient, so not likely to return data
                    conn.list_stacks(stack_status_filters=['UPDATE_IN_PROGRESS'])
                except BotoServerError as err:
                    if err.code == 'UnauthorizedOperation':
                        status = 'denied'
                    else:
                        status = 'down'

            return dict(health=dict(name=svc, status=status))
