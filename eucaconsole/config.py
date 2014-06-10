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
Pyramid configuration helpers

"""

import boto
import logging

from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.settings import asbool

from dogpile.cache import make_region
from dogpile.cache.util import sha1_mangle_key

from .i18n import custom_locale_negotiator
from .models import SiteRootFactory
from .models.auth import groupfinder, User
from .routes import urls
from .tweens import setup_tweens
from .chamext import setup_exts
from .keymgt import ensure_session_keys
from .mime import check_types
from .caches import short_term
from .caches import default_term
from .caches import long_term
from .caches import extra_long_term

try:
    from version import __version__
except ImportError:
    __version__ = 'DEVELOPMENT'


def get_configurator(settings, enable_auth=True):
    connection_debug = asbool(settings.get('connection.debug'))
    boto.set_stream_logger('boto', level=(logging.DEBUG if connection_debug else logging.CRITICAL))
    ensure_session_keys(settings)
    check_types()
    config = Configurator(root_factory=SiteRootFactory, settings=settings)
    if enable_auth:
        authn_policy = SessionAuthenticationPolicy(callback=groupfinder)
        authz_policy = ACLAuthorizationPolicy()
        config.set_authentication_policy(authn_policy)
        config.set_authorization_policy(authz_policy)
        config.set_default_permission('view')
    config.add_request_method(User.get_auth_user, 'user', reify=True)
    cache_duration = int(settings.get('static.cache.duration', 43200))
    config.add_static_view(name='static/' + __version__, path='static', cache_max_age=cache_duration)
    config.add_layout('eucaconsole.layout.MasterLayout',
                      'eucaconsole.layout:templates/master_layout.pt')
    config.add_translation_dirs('eucaconsole:locale')
    config.set_locale_negotiator(custom_locale_negotiator)
    for route in urls:
        config.add_route(route.name, route.pattern)
    setup_tweens(config)
    setup_exts(config)
    config.scan()

    memory_cache = settings.get('cache.memory')
    memory_cache_url = settings.get('cache.memory.url')
    short_term.configure(
        memory_cache,
        expiration_time = int(settings.get('cache.short_term.expire')),
        arguments = {
            'url':[memory_cache_url],
        },
    )
    default_term.configure(
        memory_cache,
        expiration_time = int(settings.get('cache.default_term.expire')),
        arguments = {
            'url':[memory_cache_url],
        },
    )
    long_term.configure(
        memory_cache,
        expiration_time = int(settings.get('cache.long_term.expire')),
        arguments = {
            'url':[memory_cache_url],
        },
    )
    extra_long_term.configure(
        memory_cache,
        expiration_time = int(settings.get('cache.extra_long_term.expire')),
        arguments = {
            'url':[memory_cache_url],
        },
    )
    return config

def main(global_config, **settings):
    """
    Main WSGI app

    The WSGI app object returned from main() is invoked from the following section in the console.ini config file...

    [app:main]
    use = egg:eucaconsole

    ...which points to eucaconsole.egg-info/entry_points.txt
    [paste.app_factory]
    main = eucaconsole.config:main

    Returns a Pyramid WSGI application"""
    app_config = get_configurator(settings)
    return app_config.make_wsgi_app()

