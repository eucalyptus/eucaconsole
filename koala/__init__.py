from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    from .routes import urls
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_layout('koala.layout.MasterLayout', 'koala.layout:templates/master_layout.pt')
    for route in urls:
        config.add_route(route.name, route.pattern)
    config.scan()
    return config.make_wsgi_app()
