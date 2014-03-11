import unittest
import tempfile
import os
import ConfigParser


class TestKeyMgt(unittest.TestCase):
    def test_generate_keyini(self):
        from eucaconsole.keymgt import generate_keyini
        ignored, filename = tempfile.mkstemp()
        try:
            generate_keyini(filename)
            config = ConfigParser.ConfigParser()
            config.read(filename)
            self.assertTrue(config.has_section('general'))
        finally:
            os.remove(filename)

    def test_ensure_session_keys(self):
        from eucaconsole.keymgt import ensure_session_keys
        ignored, filename = tempfile.mkstemp()
        os.remove(filename)
        settings = {'session.keyini': filename}

        ensure_session_keys(settings)
        key = settings.get('session.validate_key', None)
        self.assertTrue(key is not None)

        ensure_session_keys(settings)
        self.assertEqual(key, settings['session.validate_key'])

        os.remove(filename)
