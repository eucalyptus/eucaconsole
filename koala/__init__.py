"""
Main WSGI app

"""
from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .models import SiteRootFactory
from .models.auth import groupfinder
from .routes import urls
from .views.login import LoginView


def main(global_config, **settings):
    """ Return a Pyramid WSGI application"""
    authn_policy = SessionAuthenticationPolicy(callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=SiteRootFactory, settings=settings)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('view')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_layout('koala.layout.MasterLayout', 'koala.layout:templates/master_layout.pt')
    for route in urls:
        config.add_route(route.name, route.pattern)
    config.scan()
    return config.make_wsgi_app()
