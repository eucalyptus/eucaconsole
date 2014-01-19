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
def snapshot_dialogs(context, request, snapshot=None, snapshot_name=None, landingpage=False,
                     delete_form=None, register_form=None):
    """Modal dialogs for Snapshot landing and detail page."""
    return dict(
        snapshot=snapshot,
        snapshot_name=snapshot_name,
        landingpage=landingpage,
        delete_form=delete_form,
        register_form=register_form,
    )


@panel_config('instance_dialogs', renderer='../templates/dialogs/instance_dialogs.pt')
def instance_dialogs(context, request, instance=None, instance_name=None, landingpage=False, start_form=None,
                     stop_form=None, reboot_form=None, terminate_form=None):
    """Modal dialogs for Instance landing and detail page."""
    return dict(
        instance=instance,
        instance_name=instance_name,
        landingpage=landingpage,
        start_form=start_form,
        stop_form=stop_form,
        reboot_form=reboot_form,
        terminate_form=terminate_form,
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


@panel_config('create_alarm_dialog', renderer='../templates/dialogs/create_alarm_dialog.pt')
def create_alarm_dialog(context, request, alarm_form=None, modal_size='medium'):
    """Create alarm dialog page."""
    return dict(
        alarm_form=alarm_form,
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

