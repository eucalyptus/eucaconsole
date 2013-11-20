"""
Panels (reusable, parameterized template snippets) used across the app.

See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html#using-panels
"""
from pyramid_layout.panel import panel_config




@panel_config('inline_form_field', renderer='../templates/panels/inline_form_field_row.pt')
def inline_form_field(context, request, field=None, html_attrs=None):
    html_attrs = html_attrs or {}
    error_msg = getattr(field, 'error_msg', None)
    return dict(field=field, error_msg=error_msg, html_attrs=html_attrs)

