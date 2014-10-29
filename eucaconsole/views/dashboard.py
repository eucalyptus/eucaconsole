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
Pyramid views for Dashboard

"""
import simplejson as json

from pyramid.view import view_config
from boto.exception import BotoServerError

from ..forms import ChoicesManager
from . import BaseView
from ..i18n import _
from . import boto_error_handler

TILE_MASTER_LIST = [
    ('instances-running', 'Running instances'),
    ('instances-stopped', 'Stopped instances'),
    ('scaling-groups', 'Instances in scaling groups'),
    ('elastic-ips', 'Elastic IPs'),
    ('volumes', 'Volumes'),
    ('snapshots', 'Snapshots'),
    ('buckets', 'Buckets (S3)'),
    ('security-groups', 'Security groups'),
    ('key-pairs', 'Key pairs'),
    ('accounts', 'Accounts'),
    ('users', 'Users'),
    ('groups', 'Groups'),
    ('roles', 'Roles'),
    ('health', 'Service status')
]


class DashboardView(BaseView):

    def __init__(self, request):
        super(DashboardView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()

    @view_config(route_name='dashboard', request_method='GET', renderer='../templates/dashboard.pt')
    def dashboard_home(self):
        availability_zones = []
        with boto_error_handler(self.request):
            region = self.request.session.get('region')
            availability_zones = ChoicesManager(self.conn).get_availability_zones(region)
        tiles = self.request.cookies.get("{0}_dash_order".format(
            self.request.session['account' if self.request.session['cloud_type'] == 'euca' else 'access_id']))
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
        )

    def get_controller_options_json(self):
        services=[
            dict(name=_(u'Compute'), status=''),
            dict(name=_(u'Object Storage'), status=''),
            dict(name=_(u'Auto Scaling'), status=''),
            dict(name=_(u'Elastic Load Balancing'), status=''),
            dict(name=_(u'CloudWatch'), status=''),
        ]
        session = self.request.session
        if session['cloud_type'] == 'euca':
            services.append(dict(name=_(u'Identity & Access Mgmt'), status=''))
        return BaseView.escape_json(json.dumps({
            'json_items_url': self.request.route_path('dashboard_json'),
            'services': services,
            'service_status_url': self.request.route_path('service_status_json'),
            'cloud_type': self.cloud_type,
            'account_display_name': self.get_account_display_name(),
        }))


class DashboardJsonView(BaseView):
    @view_config(route_name='dashboard_json', request_method='GET', renderer='json')
    def dashboard_json(self):
        ec2_conn = self.get_connection()

        # Fetch availability zone if set
        zone = self.request.params.get('zone')
        filters = {}
        if zone:
            filters = {'availability-zone': zone}

        # Instances counts
        instances_total_count = instances_running_count = instances_stopped_count = instances_scaling_count = 0

        # Get list of tiles so we can fetch only data for tiles the user is showing
        tiles = self.request.cookies.get("{0}_dash_order".format(
            self.request.session['account' if self.request.session['cloud_type'] == 'euca' else 'access_id']))
        if tiles is None:
            tiles = ','.join([tile for (tile, label) in TILE_MASTER_LIST])
        with boto_error_handler(self.request):
            if ('instances-running' or 'instances-stopped' or 'scaling-groups') in tiles:
                for instance in ec2_conn.get_only_instances(filters=filters):
                    instances_total_count += 1
                    if instance.tags.get('aws:autoscaling:groupName'):
                        instances_scaling_count += 1
                    if instance.state == u'running':
                        instances_running_count += 1
                    elif instance.state == u'stopped':
                        instances_stopped_count += 1

            # Volume/snapshot counts
            volumes_count = len(ec2_conn.get_all_volumes(filters=filters)) if 'volumes' in tiles else 0
            snapshots_count = len(ec2_conn.get_all_snapshots(owner='self')) if 'snapshots' in tiles else 0
            s3_conn = self.get_connection(conn_type="s3")
            buckets_count = len(s3_conn.get_all_buckets()) if 'buckets' in tiles else 0

            # Security groups, key pairs, IP addresses
            securitygroups_count = len(ec2_conn.get_all_security_groups()) if 'security-groups' in tiles else 0
            keypairs_count = len(ec2_conn.get_all_key_pairs()) if 'key-pairs' in tiles else 0
            elasticips_count = len(ec2_conn.get_all_addresses()) if 'elastic-ips' in tiles else 0

            #TODO: catch errors in this block and turn iam health off
            # IAM counts
            accounts_count = 0
            users_count = 0
            groups_count = 0
            roles_count = 0
            session = self.request.session
            if session['cloud_type'] == 'euca':
                if session['username'] == 'admin':
                    iam_conn = self.get_connection(conn_type="iam")
                    if session['account_access']:
                        accounts_count = len(iam_conn.get_response(
                            'ListAccounts', params={}, list_marker='Accounts').accounts)
                    users_count = len(iam_conn.get_all_users().users) if 'users' in tiles else 0
                    groups_count = len(iam_conn.get_all_groups().groups) if 'groups' in tiles else 0
                    roles_count = len(iam_conn.list_roles().roles) if 'roles' in tiles else 0

            return dict(
                instance_total=instances_total_count,
                instances_running=instances_running_count,
                instances_stopped=instances_stopped_count,
                instances_scaling=instances_scaling_count,
                volumes=volumes_count,
                snapshots=snapshots_count,
                buckets=buckets_count,
                securitygroups=securitygroups_count,
                keypairs=keypairs_count,
                eips=elasticips_count,
                accounts=accounts_count,
                users=users_count,
                groups=groups_count,
                roles=roles_count,
                health = dict(name=_(u'Compute'), status='up'),  # this determined client-side
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
                except BotoServerError:
                    status = 'down'
            elif svc == _(u'Auto Scaling'):
                conn = self.get_connection(conn_type="autoscale")
                try:
                    conn.get_all_groups(max_records=1)
                except BotoServerError:
                    status = 'down'
            elif svc == _(u'Elastic Load Balancing'):
                conn = self.get_connection(conn_type="elb")
                try:
                    conn.get_all_load_balancers()
                except BotoServerError:
                    status = 'down'
            elif svc == _(u'CloudWatch'):
                conn = self.get_connection(conn_type="cloudwatch")
                try:
                    conn.list_metrics(namespace="AWS/EC2")
                except BotoServerError:
                    status = 'down'
            elif svc == _(u'Identiy & Access Mgmt'):
                conn = self.get_connection(conn_type="iam")
                try:
                    conn.get_all_groups(path_prefix="/notlikely")
                except BotoServerError:
                    status = 'down'

            return dict(health=dict(name=svc, status=status))
