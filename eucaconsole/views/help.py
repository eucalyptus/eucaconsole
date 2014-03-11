"""
Help Panels (reusable, parameterized template snippets) used across the app.

See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html#using-panels

"""
from pyramid_layout.panel import panel_config

@panel_config('help_ipaddresses', renderer='../templates/help/help_ipaddresses.pt')
def help_ipaddresses(context, request, display):
    return dict(display=display)

@panel_config('help_keypairs', renderer='../templates/help/help_keypairs.pt')
def help_keypairs(context, request, display):
    return dict(display=display)

@panel_config('help_securitygroups', renderer='../templates/help/help_securitygroups.pt')
def help_securitygroups(context, request, display):
    return dict(display=display)

@panel_config('help_images', renderer='../templates/help/help_images.pt')
def help_images(context, request, display, instance_create_url=''):
    return dict(display=display, instance_create_url=instance_create_url)

@panel_config('help_instances', renderer='../templates/help/help_instances.pt')
def help_instances(context, request, display, instance_name='default', instance_key_name='', instance_ip_address=''):
    return dict(display=display, instance_name=instance_name, instance_key_name=instance_key_name, instance_ip_address=instance_ip_address)

@panel_config('help_volumes', renderer='../templates/help/help_volumes.pt')
def help_volumes(context, request, display, snapshot_url=''):
    return dict(display=display, snapshot_url=snapshot_url)

@panel_config('help_snapshots', renderer='../templates/help/help_snapshots.pt')
def help_snapshots(context, request, display):
    return dict(display=display)

@panel_config('help_launchconfigs', renderer='../templates/help/help_launchconfigs.pt')
def help_launchconfigs(context, request, display):
    return dict(display=display)

@panel_config('help_scalinggroups', renderer='../templates/help/help_scalinggroups.pt')
def help_scalinggroups(context, request, display):
    return dict(display=display)

@panel_config('help_groups', renderer='../templates/help/help_groups.pt')
def help_groups(context, request, display):
    return dict(display=display)

@panel_config('help_users', renderer='../templates/help/help_users.pt')
def help_users(context, request, display):
    return dict(display=display)

