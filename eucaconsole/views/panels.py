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
Panels (reusable, parameterized template snippets) used across the app.

See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html#using-panels

"""
from operator import itemgetter

import simplejson as json

from wtforms.fields import IntegerField
from wtforms.validators import Length
from pyramid_layout.panel import panel_config

from ..constants.securitygroups import RULE_PROTOCOL_CHOICES, RULE_ICMP_CHOICES
from ..views import BaseView


@panel_config('top_nav', renderer='../templates/panels/top_nav.pt')
def top_nav(context, request, off_canvas=False):
    """ Top nav bar panel"""
    return dict(
        off_canvas=off_canvas
    )


@panel_config('landingpage_filters', renderer='../templates/panels/landingpage_filters.pt')
def landingpage_filters(context, request, filters_form=None):
    """Landing page filters form"""
    return dict(
        filters_form=filters_form,
    )


@panel_config('form_field', renderer='../templates/panels/form_field_row.pt')
def form_field_row(context, request, field=None, reverse=False, leftcol_width=4, rightcol_width=8,
                   inline='', ng_attrs=None, **kwargs):
    """ Widget for a singe form field row.
        The left/right column widths are Zurb Foundation grid units.
            e.g. leftcol_width=3 would set column for labels with a wrapper of <div class="small-3 columns">...</div>
        Pass any HTML attributes to this widget as keyword arguments.
            e.g. ${panel('form_field', field=the_field, readonly='readonly')}
    """
    html_attrs = {}
    error_msg = kwargs.get('error_msg') or getattr(field, 'error_msg', None) 

    # Add required="required" HTML attribute to form field if any "required" validators
    if field.flags.required:
        html_attrs['required'] = 'required'

    # Add appropriate HTML attributes based on validators
    for validator in field.validators:
        # Add maxlength="..." HTML attribute to form field if any length validators
        # If we have multiple Length validators, the last one wins
        if isinstance(validator, Length):
            html_attrs['maxlength'] = validator.max

    # Add HTML attributes based on field type (e.g. IntegerField)
    if isinstance(field, IntegerField):
        html_attrs['pattern'] = 'integer'  # Uses Zurb Foundation Abide's 'integer' named pattern
        html_attrs['type'] = 'number'  # Use input type="number" for IntegerField inputs
        html_attrs['min'] = kwargs.get('min', 0)

    # Add any passed kwargs to field's HTML attributes
    for key, value in kwargs.items():
        html_attrs[key] = value

    # Add AngularJS attributes
    # A bit of a hack since we can't pass ng-model='foo' to the form_field panel
    # So instead we pass ng_attrs={'model': 'foo'} to the form field
    # e.g. ${panel('form_field', field=volume_form['snapshot_id'], ng_attrs={'model': 'snapshot_id'}, **html_attrs)}
    if ng_attrs:
        for ngkey, ngvalue in ng_attrs.items():
            html_attrs['ng-{0}'.format(ngkey)] = ngvalue

    return dict(
        field=field, error_msg=error_msg, html_attrs=html_attrs, inline=inline, 
        leftcol_width=leftcol_width, rightcol_width=rightcol_width, reverse=reverse
    )


@panel_config('tag_editor', renderer='../templates/panels/tag_editor.pt')
def tag_editor(context, request, tags=None, leftcol_width=4, rightcol_width=8, show_name_tag=True):
    """ Tag editor panel.
        Usage example (in Chameleon template): ${panel('tag_editor', tags=security_group.tags)}
    """
    tags = tags or {}
    tags_json = BaseView.escape_json(json.dumps(tags))
    return dict(
        tags=tags,
        tags_json=tags_json,
        leftcol_width=leftcol_width,
        rightcol_width=rightcol_width,
        show_name_tag=show_name_tag,
    )


@panel_config('user_editor', renderer='../templates/panels/user_editor.pt')
def user_editor(context, request, leftcol_width=4, rightcol_width=8):
    """ User editor panel.
        Usage example (in Chameleon template): ${panel('user_editor')}
    """
    return dict(leftcol_width=leftcol_width, rightcol_width=rightcol_width)


@panel_config('policy_list', renderer='../templates/panels/policy_list.pt')
def policy_list(context, request, policies_url=None, policy_url=None, remove_url=None, update_url=None, add_url=None):
    """ User list panel.
        Usage example (in Chameleon template): ${panel('policy_list')}
    """
    return dict(policies_url=policies_url, policy_url=policy_url, remove_url=remove_url, update_url=update_url, add_url=add_url)


@panel_config('autoscale_tag_editor', renderer='../templates/panels/autoscale_tag_editor.pt')
def autoscale_tag_editor(context, request, tags=None, leftcol_width=2, rightcol_width=10):
    """ Tag editor panel for Scaling Groups.
        Usage example (in Chameleon template): ${panel('autoscale_tag_editor', tags=scaling_group.tags)}
    """
    tags = tags or []
    tags_list = []
    for tag in tags:
        tags_list.append(dict(
            name=tag.key,
            value=tag.value,
            propagate_at_launch=tag.propagate_at_launch,
        ))
    tags_json = BaseView.escape_json(json.dumps(tags_list))
    return dict(tags=tags, tags_json=tags_json, leftcol_width=leftcol_width, rightcol_width=rightcol_width)


@panel_config('securitygroup_rules', renderer='../templates/panels/securitygroup_rules.pt')
def securitygroup_rules(context, request, rules=None, groupnames=None, leftcol_width=3, rightcol_width=9):
    """ Security group rules panel.
        Usage example (in Chameleon template): ${panel('securitygroup_rules', rules=security_group.rules)}
    """
    groupnames = groupnames or []
    rules = rules or []
    rules_list = []
    for rule in rules:
        grants = [
            dict(name=g.name, owner_id=g.owner_id, group_id=g.group_id, cidr_ip=g.cidr_ip) for g in rule.grants
        ]
        rules_list.append(dict(
            ip_protocol=rule.ip_protocol,
            from_port=rule.from_port,
            to_port=rule.to_port,
            grants=grants,
        ))

    # Sort rules and choices
    rules_sorted = sorted(rules_list, key=itemgetter('from_port'))
    icmp_choices_sorted = sorted(RULE_ICMP_CHOICES, key=lambda tup: tup[1])

    return dict(
        rules=rules_sorted,
        groupnames=groupnames,
        rules_json=BaseView.escape_json(json.dumps(rules_list)),
        protocol_choices=RULE_PROTOCOL_CHOICES,
        icmp_choices=icmp_choices_sorted,
        remote_addr=getattr(request, 'remote_addr', ''),
        leftcol_width=leftcol_width,
        rightcol_width=rightcol_width,
    )


@panel_config('securitygroup_rules_preview', renderer='../templates/panels/securitygroup_rules_preview.pt')
def securitygroup_rules_preview(context, request, leftcol_width=3, rightcol_width=9):
    """ Security group rules preview, used in Launch Instance and Create Launch Configuration wizards.
    """
    return dict(
        leftcol_width=leftcol_width,
        rightcol_width=rightcol_width,
    )


@panel_config('bdmapping_editor', renderer='../templates/panels/bdmapping_editor.pt')
def bdmapping_editor(context, request, image=None, launch_config=None, snapshot_choices=None, read_only=False):
    """ Block device mapping editor (e.g. for Launch Instance page).
        Usage example (in Chameleon template): ${panel('bdmapping_editor', image=image, snapshot_choices=choices)}
    """
    snapshot_choices = snapshot_choices or []
    bdm_dict = {}
    if image is not None:
        bdm_object = image.block_device_mapping
        print "BDM OBJECT: ",  bdm_object
        for key, device in bdm_object.items():
            print "Volume Type: " , device.volume_type
            bdm_dict[key] = dict(
                is_root = True if get_root_device_name(image)==key else False,
                volume_type=device.volume_type,
                virtual_name=device.ephemeral_name,
                snapshot_id=device.snapshot_id,
                size=device.size,
                delete_on_termination=device.delete_on_termination,
            )
    if launch_config is not None:
        bdm_list = launch_config.block_device_mappings
        for bdm in bdm_list:
            if bdm.device_name in bdm_dict.keys():
                continue
            ebs = bdm.ebs
            bdm_dict[bdm.device_name] = dict(
                is_root = False,  # because we can't redefine root in a launch config
                volume_type=getattr(device, 'volume_type'),
                snapshot_id=getattr(ebs, 'snapshot_id'),
                size=getattr(ebs, 'volume_size'),
                delete_on_termination=getattr(ebs, 'delete_on_termination', False),
            )
    bdm_json = json.dumps(bdm_dict)
    return dict(image=image, snapshot_choices=snapshot_choices, bdm_json=bdm_json, read_only=read_only)


def get_root_device_name(img):
    return img.root_device_name.replace('&#x2f;', '/').replace(
        '&#x2f;', '/') if img.root_device_name is not None else '/dev/sda'


@panel_config('image_picker', renderer='../templates/panels/image_picker.pt')
def image_picker(context, request, image=None, images_json_endpoint=None, filters_form=None,
                 maxheight='800px', owner_choices=None, prefix_route='instance_create'):
    """ Reusable Image picker widget (e.g. for Launch Instance page, step 1).
        Usage example (in Chameleon template): ${panel('image_picker')}
    """
    return dict(
        image=image,
        filters_form=filters_form,
        images_json_endpoint=images_json_endpoint,
        maxheight=maxheight,
        owner_choices=owner_choices,
        prefix_route=prefix_route,
    )


@panel_config('policy_generator', renderer='../templates/policies/policy_generator.pt')
def policy_generator(context, request, policy_actions=None, create_form=None, resource_choices=None):
    """IAM Policy generator"""
    policy_actions = policy_actions or {}
    resource_choices = resource_choices or {}
    return dict(
        policy_actions=policy_actions,
        create_form=create_form,
        instance_choices=resource_choices.get('instances'),
        image_choices=resource_choices.get('images'),
        volume_choices=resource_choices.get('volumes'),
        snapshot_choices=resource_choices.get('snapshots'),
        security_group_choices=resource_choices.get('security_groups'),
        key_pair_choices=resource_choices.get('key_pairs'),
        vm_type_choices=resource_choices.get('vm_types'),
        availability_zone_choices=resource_choices.get('availability_zones'),
    )


@panel_config('quotas_panel', renderer='../templates/users/quotas.pt')
def quotas_panel(context, request, quota_form=None, quota_err=None):
    """quota form for 2 different user pages."""
    return dict(
        quota_form=quota_form,
        quota_err=quota_err,
    )


@panel_config('securitygroup_rules_landingpage', renderer='../templates/panels/securitygroup_rules_landingpage.pt')
def securitygroup_rules_landingpage(context, request, tile_view=False):
    return dict(
        tile_view=tile_view,
    )
