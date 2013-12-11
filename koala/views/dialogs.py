"""
Panels for modal dialogs reused across the landing page and detail page for a given resource.

See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html#using-panels

"""
from pyramid_layout.panel import panel_config


@panel_config('ipaddress_dialogs', renderer='../templates/dialogs/ipaddress_dialogs.pt')
def ipaddress_dialogs(context, request, eip=None, landingpage=False,
                      associate_form=None, disassociate_form=None, release_form=None):
    """ Modal dialogs for Elastic IP landing and detail page."""
    return dict(
        eip=eip,
        landingpage=landingpage,
        associate_form=associate_form,
        disassociate_form=disassociate_form,
        release_form=release_form,
    )
