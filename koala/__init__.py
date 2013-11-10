"""
Main WSGI app

The WSGI app object returned from main() is invoked from the following section in the console.ini config file...

[app:main]
use = egg:koala

...which points to koala.egg-info/entry_points.txt
[paste.app_factory]
main = koala:main

"""
from .config import get_configurator


def main(global_config, **settings):
    """Return a Pyramid WSGI application"""
    app_config = get_configurator(settings)
    return app_config.make_wsgi_app()
