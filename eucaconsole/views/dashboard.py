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
from pyramid.view import view_config
from boto.exception import BotoServerError

from ..forms import ChoicesManager
from . import BaseView
from ..i18n import _
from . import boto_error_handler


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
        return dict(
            availability_zones=availability_zones
        )


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

        with boto_error_handler(self.request):
            for instance in ec2_conn.get_only_instances(filters=filters):
                instances_total_count += 1
                if instance.tags.get('aws:autoscaling:groupName'):
                    instances_scaling_count += 1
                if instance.state == u'running':
                    instances_running_count += 1
                elif instance.state == u'stopped':
                    instances_stopped_count += 1

            # Volume/snapshot counts
            volumes_count = len(ec2_conn.get_all_volumes(filters=filters))
            snapshots_count = len(ec2_conn.get_all_snapshots(owner='self'))

            # Security groups, key pairs, IP addresses
            securitygroups_count = len(ec2_conn.get_all_security_groups())
            keypairs_count = len(ec2_conn.get_all_key_pairs())
            elasticips_count = len(ec2_conn.get_all_addresses())

            #TODO: catch errors in this block and turn iam health off
            # IAM counts
            users_count = 0
            groups_count = 0
            roles_count = 0
            session = self.request.session
            if session['cloud_type'] == 'euca':
                if session['username'] == 'admin':
                    iam_conn = self.get_connection(conn_type="iam")
                    users_count = len(iam_conn.get_all_users().users)
                    groups_count = len(iam_conn.get_all_groups().groups)
                    roles_count = len(iam_conn.list_roles().roles)

            return dict(
                instance_total=instances_total_count,
                instances_running=instances_running_count,
                instances_stopped=instances_stopped_count,
                instances_scaling=instances_scaling_count,
                volumes=volumes_count,
                snapshots=snapshots_count,
                securitygroups=securitygroups_count,
                keypairs=keypairs_count,
                eips=elasticips_count,
                users=users_count,
                groups=groups_count,
                roles=roles_count,
                health = [
                    dict(name=_(u'Compute'), up=True),  # this determined client-side
                ],
            )

    @view_config(route_name='service_status_json', request_method='GET', renderer='json')
    def service_status_json(self):
        ec2_conn = self.get_connection()
        with boto_error_handler(self.request):
            #TODO: add s3 health
            s3 = True
            conn = self.get_connection(conn_type="s3")
            try:
                conn.get_all_buckets()
            except BotoServerError:
                s3 = False
            autoscaling = True
            conn = self.get_connection(conn_type="autoscale")
            try:
                conn.get_all_groups(max_records=1)
            except BotoServerError:
                autoscaling = False
            elb = True
            conn = self.get_connection(conn_type="elb")
            try:
                conn.get_all_load_balancers()
            except BotoServerError:
                elb = False
            cloudwatch = True
            conn = self.get_connection(conn_type="cloudwatch")
            try:
                conn.list_metrics(namespace="AWS/EC2")
            except BotoServerError:
                cloudwatch = False
            health=[
                dict(name=_(u'Object Storage'), up=s3),
                dict(name=_(u'Auto Scaling'), up=autoscaling),
                dict(name=_(u'Elastic Load Balancing'), up=elb),
                dict(name=_(u'CloudWatch'), up=cloudwatch),
            ]
            session = self.request.session
            if session['cloud_type'] == 'euca':
                iam = True
                conn = self.get_connection(conn_type="iam")
                try:
                    conn.get_all_groups(path_prefix="/notlikely")
                except BotoServerError:
                    cloudwatch = False
                health.append(dict(name=_(u'Identity & Access Mgmt'), up=iam))


            return dict(health=health)
