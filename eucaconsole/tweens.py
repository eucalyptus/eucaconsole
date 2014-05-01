import os


def setup_tweens(config):
    """Since tweens order is important this function will
    take care of proper ordering"""

    config.add_tween('eucaconsole.tweens.https_tween_factory')
    config.add_tween('eucaconsole.tweens.request_id_tween_factory')
    config.add_tween('eucaconsole.tweens.CTHeadersTweenFactory')


def https_tween_factory(handler, registry):
    def tween(request):
        response = handler(request)
        if request.environ.get('HTTP_X_FORWARDED_PROTO') == 'https':
            request.scheme = 'https'
        return response
    return tween


def request_id_tween_factory(handler, registry):
    def tween(request):
        request.id = os.urandom(16).encode('base64').rstrip('=\n')
        response = handler(request)
        return response
    return tween


class CTHeadersTweenFactory(object):
    '''Tween factory for ensuring certain response headers are set iff content
    type is mapped.
    '''

    header_map = {
        'application/json': {
            'CACHE-CONTROL': 'NO-CACHE',
            'PRAGMA': 'NO-CACHE',
        },
        'text/html': {
            'a': 'b',
            'X-FRAME-OPTIONS': 'SAMEORIGIN',
            'CACHE-CONTROL': 'NO-CACHE',
            'PRAGMA': 'NO-CACHE',
        },
    }

    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        response = self.handler(request)
        ct = response.content_type
        map = self.header_map.get(ct.strip().lower(), None)
        if map:
            for name, value in map.items():
                response.headers[name] = value
        return response
