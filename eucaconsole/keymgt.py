import sys
from random import SystemRandom
import stat
import os
import string
import ConfigParser

random = SystemRandom()


def generate_keyini(target):
    ini = ConfigParser.ConfigParser()
    validate_key = ''.join(random.choice(string.ascii_letters + string.digits)
                           for x in range(random.randrange(30, 40)))
    encrypt_key = ''.join(random.choice(string.ascii_letters + string.digits)
                          for x in range(random.randrange(30, 40)))
    ini.add_section('general')
    ini.set('general', 'session.validate_key', validate_key)
    ini.set('general', 'session.encrypt_key', encrypt_key)

    if os.path.exists(target):
        os.remove(target)

    # using this method of creating the file as
    # os.umask() was showing bizarre results
    f = os.open(target,
                os.O_RDWR | os.O_CREAT,
                stat.S_IREAD | stat.S_IWRITE)
    os.close(f)
    with open(target, 'a') as f:
        ini.write(f)

    return ini


def ensure_session_keys(settings):
    source = settings.get('session.keyini', 'session-keys.ini')
    if not os.path.exists(source):
        ini = generate_keyini(source)
    else:
        ini = ConfigParser.ConfigParser()
        with open(source) as f:
            ini.readfp(f)

    settings['session.validate_key'] = ini.get(
        'general', 'session.validate_key')
    settings['session.encrypt_key'] = ini.get(
        'general', 'session.encrypt_key')


def main(args):
    if len(args) == 0:
        print
        print 'USAGE: %s <inifile>' % sys.argv[0]
        print
        print 'This command is used to generate an ini file containing keys suitable for Beaker'
        print
        return

    enerate_keyini(args[0])

if __name__ == '__main__':
    main(sys.argv[1:])
