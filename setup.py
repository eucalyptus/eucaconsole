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

import os

from distutils.command.build_py import build_py
from distutils.command.sdist import sdist
from setuptools import setup, find_packages

from eucaconsole import __version__


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

class build_py_with_git_version(build_py):
    '''Like build_py, but also hardcoding the version in version.__version__
       so it's consistent even outside of the source tree'''

    def build_module(self, module, module_file, package):
        build_py.build_module(self, module, module_file, package)
        print module, module_file, package
        if module == 'version' and '.' not in package:
            version_line = "__version__ = '{0}'\n".format(__version__)
            old_ver_name = self.get_module_outfile(self.build_lib, (package,),
                                                    module)
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
    '''Like sdist, but also hardcoding the version in version.__version__ so
       it's consistent even outside of the source tree'''

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

requires = [
    'beaker >= 1.5.4',
    'boto >= 2.27.0',
    'chameleon >= 2.5.3',
    'gevent >= 0.13.8',  # Note: gevent 1.0 no longer requires libevent, it bundles libev instead
    # 'greenlet >= 0.3.1',
    'gunicorn >= 18.0',
    'M2Crypto >= 0.20.2',
    'markupsafe >= 0.9.2',
    'pycrypto >= 2.0.1',
    'Paste >= 1.7.4',
    'pyramid >= 1.4',
    'pyramid_beaker >= 0.8',
    'pyramid_chameleon >= 0.1',
    'pyramid_layout <= 0.8',
    'python-dateutil >= 1.4.1',  # Don't use 2.x series unless on Python 3
    'simplejson >= 2.0.9',
    'WTForms >= 1.0.2',
]

i18n_extras = [
    'Babel',
    'lingua == 1.6',
]

dev_extras = [
    'pyramid_debugtoolbar',
    'waitress',
]

message_extractors = {'eucaconsole': [
    ('**.py', 'lingua_python', None),
    ('**.pt', 'lingua_xml', None),
]}

setup(
    name='eucaconsole',
    version='4.0.1',
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
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=[],
    extras_require={
        'i18n': i18n_extras,
        'dev': dev_extras,
    },
    message_extractors=message_extractors,
    test_suite="tests",
    entry_points="""\
    [paste.app_factory]
    main = eucaconsole.config:main
    """,
    cmdclass={'build_py': build_py_with_git_version,
              'sdist': sdist_with_git_version}
)
