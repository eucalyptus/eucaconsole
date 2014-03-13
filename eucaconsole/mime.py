import mimetypes


def check_types():
    if mimetypes.guess_type('far.svg') == (None, None):
        mimetypes.add_type('image/svg+xml', 'svg')
