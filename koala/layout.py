"""
Layout configuration via pyramid_layout
See http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html

"""
from beaker.cache import cache_region
from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.settings import asbool

from .constants import AWS_REGIONS


class MasterLayout(object):
    site_title = "Eucalyptus Management Console"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.home_url = request.application_url
        self.help_url = request.registry.settings.get('help.url')
        self.aws_enabled = asbool(request.registry.settings.get('aws.enabled'))
        self.aws_regions = AWS_REGIONS
        self.default_region = request.registry.settings.get('aws.default.region')
        self.cloud_type = request.session.get('cloud_type')
        self.selected_region = self.request.session.get('region', self.default_region)
        self.selected_region_label = self.get_selected_region_label(self.selected_region)
        self.username_label = self.request.session.get('username_label')

    @staticmethod
    @cache_region('extra_long_term', 'selected_region_label')
    def get_selected_region_label(region_name):
        """Get the label from the selected region, pulling from Beaker cache"""
        regions = [reg for reg in AWS_REGIONS if reg.get('name') == region_name]
        if regions:
            return regions[0].get('label')
        return ''

    @reify
    def global_macros(self):
        renderer = get_renderer("templates/macros.pt")
        return renderer.implementation().macros
