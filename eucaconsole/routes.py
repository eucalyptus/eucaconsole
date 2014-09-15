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
URL dispatch routes

The route names and patterns are listed here.
The routes are wired up to view callables via the view_config decorator, which attaches a view to the route_name.

For example, the 'instances' route name is connected to the Instances landing page as follows...

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt')
    def instances_landing(self):
        pass

"""
from collections import namedtuple


# Simple container to hold a route name and pattern
Route = namedtuple('Route', ['name', 'pattern'])

urls = [
    # Dashboard #####
    Route(name='dashboard', pattern='/'),
    Route(name='dashboard_json', pattern='/dashboard/json'),
    Route(name='service_status_json', pattern='/status/json'),

    # Login/logout #####
    Route(name='login', pattern='/login'),
    Route(name='logout', pattern='/logout'),
    Route(name='managecredentials', pattern='/managecredentials'),
    Route(name='changepassword', pattern='/changepassword'),

    # Common #####
    Route(name='region_select', pattern='/region/select'),
    Route(name='file_download', pattern='/_getfile'),

    # Images #####
    Route(name='images', pattern='/images'),
    Route(name='images_json', pattern='/images/json'),
    Route(name='image_view', pattern='/images/{id}'),
    Route(name='image_json', pattern='/images/{id}/json'),
    Route(name='image_state_json', pattern='/images/{id}/state/json'),
    Route(name='image_update', pattern='/images/{id}/update'),
    Route(name='image_deregister', pattern='/images/{id}/deregister'),
    Route(name='image_cancel', pattern='/images/{id}/cancel'),

    # Instances #####
    # Landing page
    Route(name='instances', pattern='/instances'),
    Route(name='instances_json', pattern='/instances/json'),
    Route(name='instances_start', pattern='/instances/start'),
    Route(name='instances_stop', pattern='/instances/stop'),
    Route(name='instances_reboot', pattern='/instances/reboot'),
    Route(name='instances_terminate', pattern='/instances/terminate'),
    Route(name='instances_batch_terminate', pattern='/instances/batch-terminate'),
    Route(name='instances_associate', pattern='/instances/associate'),
    Route(name='instances_disassociate', pattern='/instances/disassociate'),
    # Detail page
    Route(name='instance_create', pattern='/instances/new'),
    Route(name='instance_launch', pattern='/instances/launch'),
    Route(name='instance_view', pattern='/instances/{id}'),
    Route(name='instance_json', pattern='/instances/{id}/json'),
    Route(name='instance_userdata_json', pattern='/instances/{id}/userdata'),
    Route(name='instance_more', pattern='/instances/{id}/more'),
    Route(name='instance_more_launch', pattern='/instances/{id}/more/launch'),
    Route(name='instance_update', pattern='/instances/{id}/update'),
    Route(name='instance_associate', pattern='/instances/{id}/associate'),
    Route(name='instance_disassociate', pattern='/instances/{id}/disassociate'),
    Route(name='instance_start', pattern='/instances/{id}/start'),
    Route(name='instance_stop', pattern='/instances/{id}/stop'),
    Route(name='instance_reboot', pattern='/instances/{id}/reboot'),
    Route(name='instance_terminate', pattern='/instances/{id}/terminate'),
    Route(name='instance_create_image', pattern='/instances/{id}/createimage'),
    Route(name='instance_get_password', pattern='/instances/{id}/getpassword'),  # for windows instances
    Route(name='instance_state_json', pattern='/instances/{id}/state/json'),
    Route(name='instance_ip_address_json', pattern='/instances/{id}/ipaddress/json'),
    Route(name='instance_nextdevice_json', pattern='/instances/{id}/nextdevice/json'),
    Route(name='instance_console_output_json', pattern='/instances/{id}/consoleoutput/json'),
    Route(name='instance_volumes', pattern='/instances/{id}/volumes'),
    Route(name='instance_volumes_json', pattern='/instances/{id}/volumes/json'),
    Route(name='instance_volume_attach', pattern='/instances/{id}/volumes/attach'),
    Route(name='instance_volume_detach', pattern='/instances/{id}/volumes/{volume_id}/detach'),


    # Scaling Groups #####
    # Landing page
    Route(name='scalinggroups', pattern='/scalinggroups'),
    Route(name='scalinggroups_json', pattern='/scalinggroups/json'),
    Route(name='scalinggroups_delete', pattern='/scalinggroups/delete'),
    # Detail page
    Route(name='scalinggroup_new', pattern='/scalinggroups/new'),
    Route(name='scalinggroup_create', pattern='/scalinggroups/create'),
    Route(name='scalinggroup_view', pattern='/scalinggroups/{id}'),
    Route(name='scalinggroup_delete', pattern='/scalinggroups/{id}/delete'),
    Route(name='scalinggroup_update', pattern='/scalinggroups/{id}/update'),
    Route(name='scalinggroup_instances', pattern='/scalinggroups/{id}/instances'),
    Route(name='scalinggroup_instances_json', pattern='/scalinggroups/{id}/instances/json'),
    Route(name='scalinggroup_instances_markunhealthy', pattern='/scalinggroups/{id}/instances/markunhealthy'),
    Route(name='scalinggroup_instances_terminate', pattern='/scalinggroups/{id}/instances/terminate'),
    Route(name='scalinggroup_policies', pattern='/scalinggroups/{id}/policies'),
    Route(name='scalinggroup_policy_new', pattern='/scalinggroups/{id}/policies/new'),
    Route(name='scalinggroup_policy_create', pattern='/scalinggroups/{id}/policies/create'),
    Route(name='scalinggroup_policy_delete', pattern='/scalinggroups/{id}/policies/delete'),

    # Launch Configurations #####
    # Landing page
    Route(name='launchconfigs', pattern='/launchconfigs'),
    Route(name='launchconfigs_json', pattern='/launchconfigs/json'),
    Route(name='launchconfigs_delete', pattern='/launchconfigs/delete'),
    # Detail page
    Route(name='launchconfig_new', pattern='/launchconfigs/new'),
    Route(name='launchconfig_create', pattern='/launchconfigs/create'),
    Route(name='launchconfig_delete', pattern='/launchconfigs/{id}/delete'),
    Route(name='launchconfig_view', pattern='/launchconfigs/{id}'),

    # Volumes #####
    # Landing page
    Route(name='volumes', pattern='/volumes'),
    Route(name='volumes_json', pattern='/volumes/json'),
    Route(name='volumes_delete', pattern='/volumes/delete'),
    Route(name='volumes_attach', pattern='/volumes/attach'),
    Route(name='volumes_detach', pattern='/volumes/detach'),
    # Detail page
    Route(name='volume_create', pattern='/volumes/create'),
    Route(name='volume_view', pattern='/volumes/{id}'),  # Pass id='new' to render Add Volume page
    Route(name='volume_update', pattern='/volumes/{id}/update'),
    Route(name='volume_delete', pattern='/volumes/{id}/delete'),
    Route(name='volume_attach', pattern='/volumes/{id}/attach'),
    Route(name='volume_detach', pattern='/volumes/{id}/detach'),
    Route(name='volume_state_json', pattern='/volumes/{id}/state/json'),
    Route(name='volume_snapshots', pattern='/volumes/{id}/snapshots'),
    Route(name='volume_snapshots_json', pattern='/volumes/{id}/snapshots/json'),
    Route(name='volume_snapshot_create', pattern='/volumes/{id}/snapshots/create'),
    Route(name='volume_snapshot_delete', pattern='/volumes/{id}/snapshots/{snapshot_id}/delete'),

    # Snapshots #####
    # Landing page
    Route(name='snapshots', pattern='/snapshots'),
    Route(name='snapshots_json', pattern='/snapshots/json'),
    Route(name='snapshots_delete', pattern='/snapshots/delete'),
    Route(name='snapshots_register', pattern='/snapshots/register'),
    # Detail page
    Route(name='snapshot_create', pattern='/snapshots/create'),
    Route(name='snapshot_view', pattern='/snapshots/{id}'),  # Pass id='new' to render Add Snapshot page
    Route(name='snapshot_update', pattern='/snapshots/{id}/update'),
    Route(name='snapshot_delete', pattern='/snapshots/{id}/delete'),
    Route(name='snapshot_register', pattern='/snapshots/{id}/register'),
    Route(name='snapshot_size_json', pattern='/snapshots/{id}/size/json'),
    Route(name='snapshot_state_json', pattern='/snapshots/{id}/state/json'),
    Route(name='snapshot_images_json', pattern='/snapshots/{id}/images/json'),

    # Buckets #####
    # Landing page
    Route(name='buckets', pattern='/buckets'),
    Route(name='buckets_json', pattern='/buckets/json'),
    # Contents/detail pages
    Route(name='bucket_new', pattern='/buckets/new'),
    Route(name='bucket_create', pattern='/buckets/create'),
    Route(name='bucket_contents', pattern='/bucketcontents/*subpath'),
    Route(name='bucket_keys', pattern='/bucketkeys/*subpath'),
    Route(name='bucket_details', pattern='/buckets/{name}/details'),
    Route(name='bucket_objects_count_versioning_json', pattern='/buckets/{name}/objectscount.json'),
    Route(name='bucket_update', pattern='/buckets/{name}/update'),
    Route(name='bucket_delete', pattern='/buckets/{name}/delete'),
    Route(name='bucket_delete_keys', pattern='/buckets/{name}/delete_keys'),
    Route(name='bucket_update_versioning', pattern='/buckets/{name}/updateversioning'),
    Route(name='bucket_item_details', pattern='/buckets/{name}/itemdetails/*subpath'),
    Route(name='bucket_item_update', pattern='/buckets/{name}/itemupdate/*subpath'),
    Route(name='bucket_create_folder', pattern='/buckets/{name}/createfolder/*subpath'),


    # Security Groups #####
    # Landing page
    Route(name='securitygroups', pattern='/securitygroups'),
    Route(name='securitygroups_json', pattern='/securitygroups/json'),
    Route(name='securitygroups_delete', pattern='/securitygroups/delete'),
    # Detail page
    Route(name='securitygroup_create', pattern='/securitygroups/create'),
    Route(name='securitygroup_view', pattern='/securitygroups/{id}'),  # Pass id='new' to render Add SG page
    Route(name='securitygroup_update', pattern='/securitygroups/{id}/update'),
    Route(name='securitygroup_delete', pattern='/securitygroups/{id}/delete'),

    # Key pairs #####
    # Landing page
    Route(name='keypairs', pattern='/keypairs'),
    Route(name='keypairs_json', pattern='/keypairs/json'),
    # Detail page
    Route(name='keypair_create', pattern='/keypairs/create'),
    Route(name='keypair_import', pattern='/keypairs/import'),
    Route(name='keypair_delete', pattern='/keypairs/delete'),
    Route(name='keypair_view', pattern='/keypairs/{id}'),

    # IP Addresses #####
    # Landing page
    Route(name='ipaddresses', pattern='/ipaddresses'),
    Route(name='ipaddresses_json', pattern='/ipaddresses/json'),
    Route(name='ipaddresses_associate', pattern='/ipaddresses/associate'),
    Route(name='ipaddresses_disassociate', pattern='/ipaddresses/disassociate'),
    Route(name='ipaddresses_release', pattern='/ipaddresses/release'),
    # Detail page
    Route(name='ipaddress_view', pattern='/ipaddresses/{public_ip}'),
    Route(name='ipaddress_associate', pattern='/ipaddresses/{public_ip}/associate'),
    Route(name='ipaddress_disassociate', pattern='/ipaddresses/{public_ip}/disassociate'),
    Route(name='ipaddress_release', pattern='/ipaddresses/{public_ip}/release'),

    # CloudWatch Alarms #####
    # Landing page
    Route(name='cloudwatch_alarms', pattern='/cloudwatch/alarms'),
    Route(name='cloudwatch_alarms_json', pattern='/cloudwatch/alarms/json'),
    Route(name='cloudwatch_alarms_create', pattern='/cloudwatch/alarms/create'),
    Route(name='cloudwatch_alarms_delete', pattern='/cloudwatch/alarms/delete'),

    # Accounts #####
    Route(name='accounts', pattern='/accounts'),
    Route(name='accounts_json', pattern='/accounts/json'),
    Route(name='account_new', pattern='/accounts/new'),
    Route(name='accounts_delete', pattern='/accounts/delete'),
    Route(name='account_create', pattern='/accounts/create'),
    Route(name='account_view', pattern='/accounts/{name}'),
    Route(name='account_summary_json', pattern='/accounts/{name}/summary'),
    Route(name='account_update', pattern='/accounts/{name}/update'),
    Route(name='account_delete', pattern='/accounts/{name}/delete'),
    Route(name='account_policies_json', pattern='/accounts/{name}/policies_json'),
    Route(name='account_policy_json', pattern='/accounts/{name}/policies/{policy}'),
    Route(name='account_update_policy', pattern='/accounts/{name}/policy/{policy}/save'),
    Route(name='account_delete_policy', pattern='/accounts/{name}/policy/{policy}/delete'),

    # Users #####
    Route(name='users', pattern='/users'),
    Route(name='users_json', pattern='/users/json'),
    Route(name='user_new', pattern='/users/new'),
    Route(name='user_create', pattern='/users/create'),
    Route(name='user_view', pattern='/users/{name}'),  # Pass name='new' to render Create User(s) page
    Route(name='user_summary_json', pattern='/users/{name}/summary'),
    Route(name='user_enable', pattern='/users/{name}/enable'),
    Route(name='user_disable', pattern='/users/{name}/disable'),
    Route(name='user_access_keys_json', pattern='/users/{name}/keys_json'),
    Route(name='user_groups_json', pattern='/users/{name}/groups_json'),
    Route(name='user_avail_groups_json', pattern='/users/{name}/groups_available_json'),
    Route(name='user_policies_json', pattern='/users/{name}/policies_json'),
    Route(name='user_policy_json', pattern='/users/{name}/policies/{policy}'),
    Route(name='user_update', pattern='/users/{name}/update'),
    Route(name='user_delete', pattern='/users/{name}/delete'),
    Route(name='user_delete_password', pattern='/users/{name}/deletepwd'),
    Route(name='user_random_password', pattern='/users/{name}/random'),
    Route(name='user_change_password', pattern='/users/{name}/password'),
    Route(name='user_generate_keys', pattern='/users/{name}/genkeys'),
    Route(name='user_delete_key', pattern='/users/{name}/keys/{key}/delete'),
    Route(name='user_deactivate_key', pattern='/users/{name}/keys/{key}/deactivate'),
    Route(name='user_activate_key', pattern='/users/{name}/keys/{key}/activate'),
    Route(name='user_add_to_group', pattern='/users/{name}/addgroup/{group}'),
    Route(name='user_remove_from_group', pattern='/users/{name}/removegroup/{group}'),
    Route(name='user_update_quotas', pattern='/users/{name}/quotas'),
    Route(name='user_update_policy', pattern='/users/{name}/policy/{policy}/save'),
    Route(name='user_delete_policy', pattern='/users/{name}/policy/{policy}/delete'),

    # Groups #####
    Route(name='groups', pattern='/groups'),
    Route(name='groups_json', pattern='/groups/json'),
    Route(name='groups_delete', pattern='/groups/delete'),
    Route(name='group_create', pattern='/groups/create'),
    Route(name='group_view', pattern='/groups/{name}'),
    Route(name='group_update', pattern='/groups/{name}/update'),
    Route(name='group_delete', pattern='/groups/{name}/delete'),
    Route(name='group_policies_json', pattern='/groups/{name}/policies_json'),
    Route(name='group_policy_json', pattern='/groups/{name}/policies/{policy}'),
    Route(name='group_update_policy', pattern='/groups/{name}/policy/{policy}/save'),
    Route(name='group_delete_policy', pattern='/groups/{name}/policy/{policy}/delete'),

    # Roles #####
    Route(name='roles', pattern='/roles'),
    Route(name='roles_json', pattern='/roles/json'),
    Route(name='roles_delete', pattern='/roles/delete'),
    Route(name='role_create', pattern='/roles/create'),
    Route(name='role_view', pattern='/roles/{name}'),
    Route(name='role_delete', pattern='/roles/{name}/delete'),
    Route(name='role_policies_json', pattern='/roles/{name}/policies_json'),
    Route(name='role_policy_json', pattern='/roles/{name}/policies/{policy}'),
    Route(name='role_update_policy', pattern='/roles/{name}/policy/{policy}/save'),
    Route(name='role_update_trustpolicy', pattern='/roles/{name}/trustpolicy/save'),
    Route(name='role_delete_policy', pattern='/roles/{name}/policy/{policy}/delete'),

    # IAM Policies/Permissions #####
    Route(name='iam_policy_new', pattern='/policies/new'),
    Route(name='iam_policy_create', pattern='/policies/create'),
    Route(name='iam_policy_json', pattern='/policies/canned/json'),
]


