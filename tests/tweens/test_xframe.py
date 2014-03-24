import unittest


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestXFrame(unittest.TestCase):
    def test_factory(self):
        from eucaconsole.tweens import xframe_tween_factory
        tween = xframe_tween_factory(None, None)
        self.assertTrue(callable(tween))

    def test_tween(self):
        from eucaconsole.tweens import xframe_tween_factory

        class MockHandler(object):
            def __init__(self, content_type):
                self.headers = {}
                self.content_type = content_type

            def __call__(self, request):
                return Mock(content_type=self.content_type,
                            headers=self.headers)

        # make sure non html resources aren't getting header
        tween = xframe_tween_factory(MockHandler('image/jpeg'), None)
        res = tween({})
        self.assertTrue('X_FRAME_OPTIONS' not in res.headers)

        # make sure html resources *are* getting header
        tween = xframe_tween_factory(MockHandler('text/html'), None)
        res = tween({})
        self.assertTrue('X_FRAME_OPTIONS' in res.headers)

