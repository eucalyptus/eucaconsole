"""
Panels for modal dialogs reused across the landing page and detail page for a given resource.

See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html#using-panels

"""
from pyramid_layout.panel import panel_config


@panel_config('ipaddress_dialogs', renderer='../templates/dialogs/ipaddress_dialogs.pt')
def ipaddress_dialogs(context, request, eip=None, landingpage=False,
                      associate_form=None, disassociate_form=None, release_form=None):
    """Modal dialogs for Elastic IP landing and detail page."""
    return dict(
        eip=eip,
        landingpage=landingpage,
        associate_form=associate_form,
        disassociate_form=disassociate_form,
        release_form=release_form,
    )


@panel_config('snapshot_dialogs', renderer='../templates/dialogs/snapshot_dialogs.pt')
def snapshot_dialogs(context, request, snapshot=None, snapshot_name=None, landingpage=False, volume_id=None,
                     delete_form=None, register_form=None):
    """Modal dialogs for Snapshot landing and detail page."""
    return dict(
        snapshot=snapshot,
        snapshot_name=snapshot_name,
        landingpage=landingpage,
        volume_id=volume_id,
        delete_form=delete_form,
        register_form=register_form,
    )


@panel_config('instance_dialogs', renderer='../templates/dialogs/instance_dialogs.pt')
def instance_dialogs(context, request, instance=None, instance_name=None, landingpage=False, start_form=None,
                     stop_form=None, reboot_form=None, terminate_form=None, associate_ip_form=None, disassociate_ip_form=None):
    """Modal dialogs for Instance landing and detail page."""
    return dict(
        instance=instance,
        instance_name=instance_name,
        landingpage=landingpage,
        start_form=start_form,
        stop_form=stop_form,
        reboot_form=reboot_form,
        terminate_form=terminate_form,
        associate_ip_form=associate_ip_form,
        disassociate_ip_form=disassociate_ip_form,
    )


@panel_config('terminate_instances_dialog', renderer='../templates/dialogs/terminate_instances_dialog.pt')
def terminate_instances_dialog(context, request, batch_terminate_form=None):
    """Batch-terminate instances dialog"""
    return dict(
        batch_terminate_form=batch_terminate_form,
    )


@panel_config('volume_dialogs', renderer='../templates/dialogs/volume_dialogs.pt')
def volume_dialogs(context, request, volume=None, volume_name=None, instance_name=None, landingpage=False,
                   attach_form=None, detach_form=None, delete_form=None):
    """Modal dialogs for Volume landing and detail page."""
    return dict(
        volume=volume,
        volume_name=volume_name,
        instance_name=instance_name,
        landingpage=landingpage,
        attach_form=attach_form,
        detach_form=detach_form,
        delete_form=delete_form,
    )


@panel_config('securitygroup_dialogs', renderer='../templates/dialogs/securitygroup_dialogs.pt')
def securitygroup_dialogs(context, request, security_group=None, landingpage=False, delete_form=None):
    """Modal dialogs for Security group landing and detail page."""
    return dict(
        security_group=security_group,
        landingpage=landingpage,
        delete_form=delete_form,
    )


@panel_config('create_securitygroup_dialog', renderer='../templates/dialogs/create_securitygroup_dialog.pt')
def create_securitygroup_dialog(context, request, securitygroup_form=None, security_group_names=None):
    """ Modal dialog for creating a security group."""
    return dict(
        securitygroup_form=securitygroup_form,
        security_group_names=security_group_names,
    )


@panel_config('create_alarm_dialog', renderer='../templates/dialogs/create_alarm_dialog.pt')
def create_alarm_dialog(context, request, alarm_form=None, redirect_location=None, modal_size='medium'):
    """Create alarm dialog page."""
    redirect_location = redirect_location or request.route_path('cloudwatch_alarms')
    return dict(
        alarm_form=alarm_form,
        redirect_location=redirect_location,
        modal_size=modal_size,
    )


@panel_config('keypair_dialogs', renderer='../templates/dialogs/keypair_dialogs.pt')
def keypair_dialogs(context, request, keypair=None, landingpage=False, delete_form=None):
    """ Modal dialogs for Keypair landing and detail page."""
    return dict(
        keypair=keypair,
        landingpage=landingpage,
        delete_form=delete_form,
    )


@panel_config('create_keypair_dialog', renderer='../templates/dialogs/create_keypair_dialog.pt')
def create_keypair_dialog(context, request, keypair_form=None, generate_file_form=None):
    """ Modal dialog for creating a key pair."""
    return dict(
        keypair_form=keypair_form,
        generate_file_form=generate_file_form,
    )


@panel_config('launchconfig_dialogs', renderer='../templates/dialogs/launchconfig_dialogs.pt')
def launchconfig_dialogs(context, request, launch_config=None, in_use=False, landingpage=False, delete_form=None):
    """ Modal dialogs for Launch configurations landing and detail page."""
    return dict(
        launch_config=launch_config,
        in_use=in_use,
        landingpage=landingpage,
        delete_form=delete_form,
    )

@panel_config('scalinggroup_dialogs', renderer='../templates/dialogs/scalinggroup_dialogs.pt')
def scalinggroup_dialogs(context, request, scaling_group=None, landingpage=False, delete_form=None):
    """Modal dialogs for Scaling group landing and detail page."""
    return dict(
        scaling_group=scaling_group,
        landingpage=landingpage,
        delete_form=delete_form,
    )

