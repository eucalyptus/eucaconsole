# Copyright 2013-2014 Eucalyptus Systems, Inc.
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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

    generate_keyini(args[0])

if __name__ == '__main__':
    main(sys.argv[1:])
