# -*- coding: utf-8 -*-
"""
Pyramid views for Dashboard

"""
from boto.exception import BotoServerError
from pyramid.view import view_config
from . import BaseView
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
            availability_zones = self.conn.get_all_zones()
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

            # IAM counts
            session = self.request.session
            try:
                username = session['username']
                if username == 'admin':
                    iam_conn = self.get_connection(conn_type="iam")
                    users_count = len(iam_conn.get_all_users().users)
                    groups_count = len(iam_conn.get_all_groups().groups)
                else:
                    users_count = 0
                    groups_count = 0
            except KeyError:
                users_count = 0
                groups_count = 0

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
            )
