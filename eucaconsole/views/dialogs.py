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
Panels for modal dialogs reused across the landing page and detail page for a given resource.

See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html#using-panels

"""
from pyramid_layout.panel import panel_config

from ..views import BaseView
from ..views.buckets import BucketDetailsView, FOLDER_NAME_PATTERN


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
    ng_attrs = {'model': 'instanceId', 'change': 'getDeviceSuggestion()'}
    # If landing page, build instance choices based on selected volumes availability zone (see volumes.js)
    if landingpage:
        ng_attrs['options'] = 'k as v for (k, v) in instanceChoices'
    return dict(
        volume=volume,
        volume_name=volume_name,
        instance_name=instance_name,
        landingpage=landingpage,
        attach_form=attach_form,
        detach_form=detach_form,
        delete_form=delete_form,
        ng_attrs=ng_attrs,
    )

@panel_config('user_dialogs', renderer='../templates/dialogs/user_dialogs.pt')
def user_dialogs(context, request, user=None, user_name=None, landingpage=False,
                   disable_form=None, enable_form=None, delete_form=None):
    """Modal dialogs for User landing and detail page."""
    return dict(
        user=user,
        user_name=user_name,
        landingpage=landingpage,
        disable_form=disable_form,
        enable_form=enable_form,
        delete_form=delete_form,
    )

@panel_config('securitygroup_dialogs', renderer='../templates/dialogs/securitygroup_dialogs.pt')
def securitygroup_dialogs(context, request, security_group=None, landingpage=False, delete_form=None):
    """Modal dialogs for Security group landing and detail page."""
    return dict(
        security_group=security_group,
        security_group_name=BaseView.escape_braces(security_group.name) if security_group else '',
        landingpage=landingpage,
        delete_form=delete_form,
    )


@panel_config('create_securitygroup_dialog', renderer='../templates/dialogs/create_securitygroup_dialog.pt')
def create_securitygroup_dialog(context, request, securitygroup_form=None):
    """ Modal dialog for creating a security group."""
    return dict(
        securitygroup_form=securitygroup_form,
    )


@panel_config('create_alarm_dialog', renderer='../templates/dialogs/create_alarm_dialog.pt')
def create_alarm_dialog(context, request, alarm_form=None, redirect_location=None,
                        modal_size='medium', metric_unit_mapping=None):
    """Create alarm dialog page."""
    redirect_location = redirect_location or request.route_path('cloudwatch_alarms')
    return dict(
        alarm_form=alarm_form,
        redirect_location=redirect_location,
        modal_size=modal_size,
        metric_unit_mapping=metric_unit_mapping,
    )


@panel_config('keypair_dialogs', renderer='../templates/dialogs/keypair_dialogs.pt')
def keypair_dialogs(context, request, keypair=None, landingpage=False, delete_form=None):
    """ Modal dialogs for Keypair landing and detail page."""
    return dict(
        keypair=keypair,
        keypair_name=BaseView.escape_braces(keypair.name) if keypair else '',
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
        launch_config_name=BaseView.escape_braces(launch_config.name) if launch_config else '',
        in_use=in_use,
        landingpage=landingpage,
        delete_form=delete_form,
    )


@panel_config('scalinggroup_dialogs', renderer='../templates/dialogs/scalinggroup_dialogs.pt')
def scalinggroup_dialogs(context, request, scaling_group=None, landingpage=False, delete_form=None):
    """Modal dialogs for Scaling group landing and detail page."""
    return dict(
        scaling_group=scaling_group,
        scaling_group_name=BaseView.escape_braces(scaling_group.name) if scaling_group else '',
        landingpage=landingpage,
        delete_form=delete_form,
    )


@panel_config('account_dialogs', renderer='../templates/dialogs/account_dialogs.pt')
def account_dialogs(context, request, account=None, landingpage=False, delete_form=None):
    """ Modal dialogs for Account landing and detail page."""
    return dict(
        account=account,
        landingpage=landingpage,
        delete_form=delete_form,
    )


@panel_config('group_dialogs', renderer='../templates/dialogs/group_dialogs.pt')
def group_dialogs(context, request, group=None, landingpage=False, delete_form=None):
    """ Modal dialogs for Group landing and detail page."""
    return dict(
        group=group,
        landingpage=landingpage,
        delete_form=delete_form,
    )


@panel_config('role_dialogs', renderer='../templates/dialogs/role_dialogs.pt')
def role_dialogs(context, request, role=None, landingpage=False, delete_form=None):
    """ Modal dialogs for Role landing and detail page."""
    return dict(
        role=role,
        landingpage=landingpage,
        delete_form=delete_form,
    )


@panel_config('image_dialogs', renderer='../templates/dialogs/image_dialogs.pt')
def image_dialogs(context, request, image=None, image_name_id='', landingpage=False,
                  deregister_form=None, snapshot_images_registered=0):
    """ Modal dialogs for Image landing and detail page."""
    return dict(
        image=image,
        image_name_id=image_name_id,
        landingpage=landingpage,
        deregister_form=deregister_form,
        snapshot_images_registered=snapshot_images_registered,
    )


@panel_config('bucket_delete_dialog', renderer='../templates/dialogs/bucket_delete_dialog.pt')
def bucket_delete_dialog(context, request):
    return dict()

@panel_config('bucket_dialogs', renderer='../templates/dialogs/bucket_dialogs.pt')
def bucket_dialogs(context, request, bucket=None, landingpage=False, versioning_form=None, delete_form=None):
    """ Modal dialogs for Bucket landing and detail page."""
    versioning_status = bucket.get_versioning_status() if bucket else None
    update_versioning_action = 'enable'  # Buckets that have never enabled versioning return an empty status
    if versioning_status:
        versioning_status = versioning_status.get('Versioning', 'Disabled')
        update_versioning_action = BucketDetailsView.get_versioning_update_action(versioning_status)
    return dict(
        bucket=bucket,
        bucket_name=bucket.name if bucket else '',
        versioning_status=versioning_status,
        landingpage=landingpage,
        versioning_form=versioning_form,
        delete_form=delete_form,
        update_versioning_action=update_versioning_action,
    )


@panel_config('create_folder_dialog', renderer='../templates/dialogs/create_folder_dialog.pt')
def create_folder_dialog(context, request, bucket_name=None, create_folder_form=None):
    """ Modal dialog creating a folder in a bucket."""
    return dict(
        bucket_name=bucket_name,
        create_folder_form=create_folder_form,
        folder_name_pattern=FOLDER_NAME_PATTERN,
    )

