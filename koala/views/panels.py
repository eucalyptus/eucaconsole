"""
Panels (reusable, parameterized template snippets) used across the app.

See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html#using-panels
"""
from pyramid_layout.panel import panel_config


@panel_config('form_field', renderer='../templates/panels/form_field_row.pt')
def form_field_row(context, request, field=None, html_attrs=None):
    html_attrs = html_attrs or {}
    # Add required="required" attributed to form field if any "required" validators are detected
    if field.flags.required and html_attrs.get('required') is None:
        html_attrs['required'] = 'required'
    error_msg = getattr(field, 'error_msg', None)
    return dict(field=field, error_msg=error_msg, html_attrs=html_attrs)


@panel_config('tag_editor', renderer='../templates/panels/tag_editor.pt')
def tag_editor(context, request, tags=None):
    return dict(tags=tags)

