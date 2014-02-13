"""
Pyramid configuration helpers

"""
from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .models import SiteRootFactory
from .models.auth import groupfinder, User
from .routes import urls
from .tweens import setup_tweens


def get_configurator(settings, enable_auth=True):
    config = Configurator(root_factory=SiteRootFactory, settings=settings)
    if enable_auth:
        authn_policy = SessionAuthenticationPolicy(callback=groupfinder)
        authz_policy = ACLAuthorizationPolicy()
        config.set_authentication_policy(authn_policy)
        config.set_authorization_policy(authz_policy)
        config.set_default_permission('view')
    config.add_request_method(User.get_auth_user, 'user', reify=True)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_layout('koala.layout.MasterLayout', 'koala.layout:templates/master_layout.pt')
    for route in urls:
        config.add_route(route.name, route.pattern)
    setup_tweens(config)
    config.scan()
    return config

