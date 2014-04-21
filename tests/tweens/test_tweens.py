import unittest


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class MockConfig(Mock):
    def __init__(self):
        self.tweens = []

    def add_tween(self, mpath):
        self.tweens.append(mpath)


class TestSetup(unittest.TestCase):
    def test_it(self):
        from eucaconsole.tweens import setup_tweens

        config = MockConfig()
        self.assertTrue(len(config.tweens) == 0)
        setup_tweens(config)
        self.assertTrue(len(config.tweens) > 1)


class TestHtmlHeaders(unittest.TestCase):
    def test_factory(self):
        from eucaconsole.tweens import \
            HtmlHeadersTweenFactory as factory
        tween = factory(None, None)
        self.assertTrue(callable(tween))

    def test_tween(self):
        from eucaconsole.tweens import \
            HtmlHeadersTweenFactory as factory

        class MockHandler(object):
            def __init__(self, content_type):
                self.headers = {}
                self.content_type = content_type

            def __call__(self, request):
                return Mock(content_type=self.content_type,
                            headers=self.headers)

        tween = factory(MockHandler('image/jpeg'), None)
        res = tween(None)
        for name, value in factory.html_headers.items():
            # make sure non html resources aren't getting header
            self.assertTrue(name not in res.headers)

        tween = factory(MockHandler('text/html'), None)
        res = tween(None)
        for name, value in factory.html_headers.items():
            # make sure html resources *are* getting header
            self.assertTrue(name in res.headers)
            self.assertTrue(res.headers[name] == value)
