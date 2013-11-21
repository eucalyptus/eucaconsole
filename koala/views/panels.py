"""
Panels (reusable, parameterized template snippets) used across the app.

See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html#using-panels

"""
from operator import itemgetter

try:
    import simplejson as json
except ImportError:
    import json

from pyramid_layout.panel import panel_config

from ..constants.securitygroups import RULE_PROTOCOL_CHOICES, RULE_ICMP_CHOICES


@panel_config('form_field', renderer='../templates/panels/form_field_row.pt')
def form_field_row(context, request, field=None, html_attrs=None, leftcol_width=3, rightcol_width=9):
    """ Widget for a singe form field row.
        The left/right column widths are Zurb Foundation grid units.
        e.g. leftcol_width=3 would set column for labes with a wrapper of <div class="small-3 columns">...</div>
    """
    html_attrs = html_attrs or {}
    # Add required="required" attributed to form field if any "required" validators are detected
    if field.flags.required and html_attrs.get('required') is None:
        html_attrs['required'] = 'required'
    error_msg = getattr(field, 'error_msg', None)
    return dict(
        field=field, error_msg=error_msg, html_attrs=html_attrs,
        leftcol_width=leftcol_width, rightcol_width=rightcol_width
    )


@panel_config('tag_editor', renderer='../templates/panels/tag_editor.pt')
def tag_editor(context, request, tags=None):
    """ Tag editor panel.
        Usage example (in Chameleon template): ${panel('tag_editor', tags=security_group.tags)}
    """
    tags_json = json.dumps(tags)
    return dict(tags=tags, tags_json=tags_json)


@panel_config('securitygroup_rules', renderer='../templates/panels/securitygroup_rules.pt')
def securitygroup_rules(context, request, rules=None, groupnames=None):
    """ Security group rules panel.
        Usage example (in Chameleon template): ${panel('securitygroup_rules', rules=security_group.rules)}
    """
    groupnames = groupnames or []
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
    )
