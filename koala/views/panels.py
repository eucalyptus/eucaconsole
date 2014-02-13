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
def form_field_row(context, request, field=None, reverse=False, leftcol_width=4, rightcol_width=8, inline='', ng_attrs=None, **kwargs):
    """ Widget for a singe form field row.
        The left/right column widths are Zurb Foundation grid units.
            e.g. leftcol_width=3 would set column for labels with a wrapper of <div class="small-3 columns">...</div>
        Pass any HTML attributes to this widget as keyword arguments.
            e.g. ${panel('form_field', field=the_field, readonly='readonly')}
    """
    html_attrs = {}
    error_msg = getattr(field, 'error_msg', None)

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
def tag_editor(context, request, tags=None, leftcol_width=4, rightcol_width=8):
    """ Tag editor panel.
        Usage example (in Chameleon template): ${panel('tag_editor', tags=security_group.tags)}
    """
    tags = tags or {}
    tags_json = json.dumps(tags)
    return dict(tags=tags, tags_json=tags_json, leftcol_width=leftcol_width, rightcol_width=rightcol_width)


@panel_config('user_editor', renderer='../templates/panels/user_editor.pt')
def user_editor(context, request, leftcol_width=4, rightcol_width=8):
    """ User editor panel.
        Usage example (in Chameleon template): ${panel('user_editor')}
    """
    return dict(leftcol_width=leftcol_width, rightcol_width=rightcol_width)


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
    tags_json = json.dumps(tags_list)
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
        rules_json=json.dumps(rules_list),
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
def bdmapping_editor(context, request, image=None, snapshot_choices=None):
    """ Block device mapping editor (e.g. for Launch Instance page).
        Usage example (in Chameleon template): ${panel('bdmapping_editor', image=image, snapshot_choices=choices)}
    """
    snapshot_choices = snapshot_choices or []
    bdm_dict = {}
    if image:
        bdm_object = image.block_device_mapping
        for key, device in bdm_object.items():
            bdm_dict[key] = dict(
                volume_type=device.volume_type,
                snapshot_id=device.snapshot_id,
                size=device.size,
                delete_on_termination=device.delete_on_termination,
            )
    bdm_json = json.dumps(bdm_dict)
    return dict(image=image, snapshot_choices=snapshot_choices,bdm_json=bdm_json)


@panel_config('image_picker', renderer='../templates/panels/image_picker.pt')
def image_picker(context, request, image=None, images_json_endpoint=None,
                 maxheight='800px', owner_choices=None, prefix_route='instance_create'):
    """ Reusable Image picker widget (e.g. for Launch Instance page, step 1).
        Usage example (in Chameleon template): ${panel('image_picker')}
    """
    return dict(
        image=image,
        images_json_endpoint=images_json_endpoint,
        maxheight=maxheight,
        owner_choices=owner_choices,
        prefix_route=prefix_route,
    )


@panel_config('quotas_panel', renderer='../templates/users/quotas.pt')
def quotas_panel(context, request, quota_form=None):
    """quota form for 2 different user pages."""
    return dict(
        quota_form=quota_form,
    )


@panel_config('securitygroup_rules_landingpage', renderer='../templates/panels/securitygroup_rules_landingpage.pt')
def securitygroup_rules_landingpage(context, request, tile_view=False):
    return dict(
        tile_view=tile_view,
    )
