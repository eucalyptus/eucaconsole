import unittest


class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestBraces(unittest.TestCase):
    def test_it(self):
        from eucaconsole.chamext import escape_double_braces
        f = escape_double_braces('{{ hello world }}')
        res = f(None, None)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].value.s, '&#123; hello world &#125;')
