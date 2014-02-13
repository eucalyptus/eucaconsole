
def setup_tweens(config):
    '''Since tweens order is important this function will take care
    of proper ordering'''

    config.add_tween('koala.tweens.xframe_tween_factory')


def xframe_tween_factory(handler, registry):
    def tween(request):
        response = handler(request)
        if response.content_type.strip().lower() == 'text/html':
            response.headers['X_FRAME_OPTIONS'] = 'SAMEORIGIN'
        return response
    return tween
