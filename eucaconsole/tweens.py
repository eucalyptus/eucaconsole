
def setup_tweens(config):
    '''Since tweens order is important this function will take care
    of proper ordering'''

    config.add_tween('eucaconsole.tweens.xframe_tween_factory')


def xframe_tween_factory(handler, registry):
    def tween(request):
        response = handler(request)
        if response.content_type and response.content_type.strip().lower() == 'text/html':
            response.headers['X-FRAME-OPTIONS'] = 'SAMEORIGIN'
        return response
    return tween
