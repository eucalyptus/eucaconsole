# -*- coding: utf-8 -*-
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

    # Login/logout #####
    Route(name='login', pattern='/login'),
    Route(name='logout', pattern='/logout'),
    Route(name='changepassword', pattern='/changepassword'),

    # Common #####
    Route(name='region_select', pattern='/region/select'),
    Route(name='generate_file', pattern='/_genfile'),

    # Images #####
    Route(name='images', pattern='/images'),
    Route(name='images_json', pattern='/images/json'),
    Route(name='image_view', pattern='/images/{id}'),
    Route(name='image_update', pattern='/images/{id}/update'),

    # Instances #####
    # Landing page
    Route(name='instances', pattern='/instances'),
    Route(name='instances_json', pattern='/instances/json'),
    Route(name='instances_start', pattern='/instances/start'),
    Route(name='instances_stop', pattern='/instances/stop'),
    Route(name='instances_reboot', pattern='/instances/reboot'),
    Route(name='instances_terminate', pattern='/instances/terminate'),
    # Detail page
    Route(name='instance_create', pattern='/instances/new'),
    Route(name='instance_launch', pattern='/instances/launch'),
    Route(name='instance_view', pattern='/instances/{id}'),
    Route(name='instance_more', pattern='/instances/{id}/more'),
    Route(name='instance_more_launch', pattern='/instances/{id}/more/launch'),
    Route(name='instance_update', pattern='/instances/{id}/update'),
    Route(name='instance_start', pattern='/instances/{id}/start'),
    Route(name='instance_stop', pattern='/instances/{id}/stop'),
    Route(name='instance_reboot', pattern='/instances/{id}/reboot'),
    Route(name='instance_terminate', pattern='/instances/{id}/terminate'),
    Route(name='instance_state_json', pattern='/instances/{id}/state/json'),
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
    # Detail page
    Route(name='scalinggroup_new', pattern='/scalinggroups/new'),
    Route(name='scalinggroup_create', pattern='/scalinggroups/create'),
    Route(name='scalinggroup_delete', pattern='/scalinggroups/delete'),
    Route(name='scalinggroup_view', pattern='/scalinggroups/{id}'),
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
    Route(name='launchconfig_delete', pattern='/launchconfigs/delete'),
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
    Route(name='keypair_download', pattern='/keypairs/download'),
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

    # Users #####
    Route(name='users', pattern='/users'),
    Route(name='users_json', pattern='/users/json'),
    Route(name='user_new', pattern='/users/new'),
    Route(name='user_create', pattern='/users/create'),
    Route(name='user_view', pattern='/users/{name}'), # Pass name='new' to render Create User(s) page
    Route(name='user_update', pattern='/users/{name}/update'),
    Route(name='user_delete', pattern='/users/{name}/delete'),
    Route(name='user_change_password', pattern='/users/{name}/password'),
    Route(name='user_generate_keys', pattern='/users/{name}/genkeys'),
    Route(name='user_update_quotas', pattern='/users/{name}/quotas'),

    # Groups #####
    Route(name='groups', pattern='/groups'),
    Route(name='groups_json', pattern='/groups/json'),
    Route(name='group_view', pattern='/groups/{name}'),
    Route(name='group_update', pattern='/groups/{name}/update'),
]

