# Copyright (c) 2013-2017 Ent. Services Development Corporation LP
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

import glob
import os.path
import re
import subprocess
import sys

from distutils.command.build_py import build_py
from distutils.command.sdist import sdist
from setuptools import setup, find_packages
import setuptools.command.install

from eucaconsole import __version__

DATA_DIR = os.path.join(sys.prefix, 'share')
LIBEXECDIR = os.path.join(sys.prefix, 'libexec')
SYSCONFDIR = '/etc'


def get_data_files(path, regex):
    data_files = []
    for root, _, filenames in os.walk(path, followlinks=True):
        files = []
        for filename in filenames:
            if re.match(regex, filename) is not None:
                files.append(os.path.join(root, filename))
        data_files.append((os.path.join(DATA_DIR, root), files))
    return data_files


def get_package_files(package_dir, regex):
    package_files = []
    if not package_dir.endswith('/'):
        package_dir += '/'
    for root, _, filenames in os.walk(package_dir, followlinks=True):
        files = []
        for fname in filenames:
            package_path = os.path.join(root[len(package_dir):], fname)
            if re.match(regex, package_path) is not None:
                files.append(package_path)
        package_files.extend(files)
    return package_files


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


class build_py_with_git_version(build_py):
    """Like build_py, but also hardcoding the version in version.__version__
       so it's consistent even outside of the source tree"""

    def build_module(self, module, module_file, package):
        build_py.build_module(self, module, module_file, package)
        print module, module_file, package
        if module == 'version' and '.' not in package:
            version_line = "__version__ = '{0}'\n".format(__version__)
            old_ver_name = self.get_module_outfile(self.build_lib, (package,), module)
            new_ver_name = old_ver_name + '.new'
            with open(new_ver_name, 'w') as new_ver:
                with open(old_ver_name) as old_ver:
                    for line in old_ver:
                        if line.startswith('__version__ ='):
                            new_ver.write(version_line)
                        else:
                            new_ver.write(line)
                new_ver.flush()
            os.rename(new_ver_name, old_ver_name)


class sdist_with_git_version(sdist):
    """Like sdist, but also hardcoding the version in version.__version__ so
       it's consistent even outside of the source tree"""

    def make_release_tree(self, base_dir, files):
        sdist.make_release_tree(self, base_dir, files)
        version_line = "__version__ = '{0}'\n".format(__version__)
        old_ver_name = os.path.join(base_dir, 'eucaconsole/version.py')
        new_ver_name = old_ver_name + '.new'
        with open(new_ver_name, 'w') as new_ver:
            with open(old_ver_name) as old_ver:
                for line in old_ver:
                    if line.startswith('__version__ ='):
                        new_ver.write(version_line)
                    else:
                        new_ver.write(line)
            new_ver.flush()
        os.rename(new_ver_name, old_ver_name)


class InitsysInstallData(setuptools.command.install.install):
    init_system = None  # magically populated by setuptools
    user_options = setuptools.command.install.install.user_options + [
        ('init-system=', None, ('init system to configure (systemd) [default: none]'))]

    def initialize_options(self):
        setuptools.command.install.install.initialize_options(self)
        self.init_system = ''

    def finalize_options(self):
        setuptools.command.install.install.finalize_options(self)

        if self.init_system == 'systemd':
            system_unitdir = subprocess.check_output(
                ('pkg-config', '--variable=systemdsystemunitdir', 'systemd')).strip()
            if system_unitdir:
                self.distribution.data_files.append(
                    (system_unitdir, glob.glob('systemd/units/*')))
            tmpfilesdir = subprocess.check_output(
                ('pkg-config', '--variable=tmpfilesdir', 'systemd')).strip()
            if tmpfilesdir:
                self.distribution.data_files.append(
                    (tmpfilesdir, glob.glob('systemd/tempfiles/*')))
        # Update the file list
        self.distribution.reinitialize_command('install_data', True)


requires = [
    'beaker >= 1.5.4',
    'boto >= 2.43.0',
    'botocore',
    'chameleon >= 2.5.3',
    'defusedxml >= 0.4',
    'dogpile.cache >= 0.5.3',
    # taking this out since we need gevent1 for pkg install
    # 'gevent >= 0.13.8',  # Note: gevent 1.0 no longer requires libevent, it bundles libev instead,
    # 'greenlet >= 0.3.1',
    'gunicorn >= 18.0',
    'lxml >= 3.2.1',
    'M2Crypto >= 0.20.2',
    'markupsafe >= 0.9.2',
    'pycryptopp',
    'Paste >= 1.7.4',
    'pyramid >= 1.4',
    'pyramid_beaker >= 0.8',
    'pyramid_chameleon >= 0.1',
    'pyramid_layout >= 0.8',
    'python-dateutil >= 1.4.1',  # Don't use 2.x series unless on Python 3
    'python-magic >= 0.4.6',
    'simplejson >= 2.0.9',
    'WTForms >= 1.0.2',
    'eventlet >= 0.15.2',
    'pandas >= 0.17',
]

i18n_extras = [
    'Babel',
    'lingua == 1.6',
]

dev_extras = [
    'moto == 0.4.31',
    'pylibmc',
    'pyramid_debugtoolbar',
    'waitress',
]

message_extractors = {'eucaconsole': [
    ('**.py', 'lingua_python', None),
    ('**.pt', 'lingua_xml', None),
]}


setup(
    name='eucaconsole',
    version=__version__,
    description='Eucalyptus Management Console',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Eucalyptus Systems',
    author_email='info@eucalyptus.com',
    url='http://www.eucalyptus.com',
    keywords='web pyramid pylons',
    packages=find_packages(),
    package_data={'eucaconsole': get_package_files('eucaconsole', r'^[static\|templates]\.*')},
    include_package_data=True,
    scripts=('bin/eucaconsole',),
    zip_safe=False,
    install_requires=requires,
    tests_require=[],
    extras_require={
        'i18n': i18n_extras,
        'dev': dev_extras,
    },
    message_extractors=message_extractors,
    data_files=(get_data_files("locale", r'.*\.mo$') +
                get_data_files("eucaconsole/cf-templates", r'.*\.json$') +
                [(os.path.join(SYSCONFDIR, 'eucaconsole'),
                  ['conf/console.ini', 'conf/nginx.conf'])] +
                [(os.path.join(LIBEXECDIR, 'eucaconsole'),
                  ['bin/eucaconsole-certgen',
                   'bin/eucaconsole-keygen'])]),
    test_suite="tests",
    entry_points="""\
    [paste.app_factory]
    main = eucaconsole.config:main
    """,
    cmdclass={'build_py': build_py_with_git_version,
              'install': InitsysInstallData,
              'sdist': sdist_with_git_version}
)
