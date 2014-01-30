"""
Help Panels (reusable, parameterized template snippets) used across the app.

See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html#using-panels

"""
from pyramid_layout.panel import panel_config

@panel_config('help_ipaddresses', renderer='../templates/help/help_ipaddresses.pt')
def help_ipaddresses(context, request, display):
    return dict(display=display)





