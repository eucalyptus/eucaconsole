"""
Main WSGI app

"""
from .config import get_configurator
from paste.deploy import loadapp


def main(global_config, **settings):
    """Return a Pyramid WSGI application
       Note: The WSGI app is compatible with Waitress,
             a pure Python multi-threaded Web server that is Pyramid's de facto Web server.
    """
    site_config = get_configurator(settings)
    return site_config.make_wsgi_app()


# WSGI app for gunicorn
# Run gunicorn via `gunicorn koala -w 8 -k gevent'
# See http://gunicorn.org
application = loadapp('config:console.ini', relative_to='.')

