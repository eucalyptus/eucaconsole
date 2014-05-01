import unittest


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class MockConfig(Mock):
    def __init__(self):
        self.tweens = []

    def add_tween(self, mpath):
        self.tweens.append(mpath)


class MockHandler(object):
    def __init__(self, content_type=None):
        self.headers = {}
        self.content_type = content_type

    def __call__(self, request):
        return Mock(content_type=self.content_type,
                    headers=self.headers)


class MockRequest(object):
    def __init__(self):
        self.environ = {}


class TestSetup(unittest.TestCase):
    def test_it(self):
        from eucaconsole.tweens import setup_tweens

        config = MockConfig()
        self.assertTrue(len(config.tweens) == 0)
        setup_tweens(config)
        self.assertTrue(len(config.tweens) > 1)


class TestCTHeaders(unittest.TestCase):
    def test_factory(self):
        from eucaconsole.tweens import \
            CTHeadersTweenFactory as factory
        tween = factory(None, None)
        self.assertTrue(callable(tween))

    def test_tween(self):
        from eucaconsole.tweens import \
            CTHeadersTweenFactory as factory

        tween = factory(MockHandler('image/jpeg'), None)
        res = tween(None)
        for name, value in factory.header_map['text/html'].items():
            # make sure html resources *are* getting header
            self.assertFalse(name in res.headers)

        tween = factory(MockHandler('text/html'), None)
        res = tween(None)
        for name, value in factory.header_map['text/html'].items():
            # make sure html resources *are* getting header
            self.assertTrue(name in res.headers)
            self.assertTrue(res.headers[name] == value)


class TestHTTPSTween(unittest.TestCase):
    def test_it(self):
        from eucaconsole.tweens import \
            https_tween_factory as factory
        tween = factory(MockHandler(), None)

        request = Mock(scheme=None, environ={})
        tween(request)
        self.assertTrue(request.scheme is None)

        request = Mock(scheme=None,
                       environ={'HTTP_X_FORWARDED_PROTO': 'https'})
        tween(request)
        self.assertEqual(request.scheme, 'https')
