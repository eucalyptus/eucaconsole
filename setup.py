import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    # 'Babel >= 1.3',  # Only required for generating i18n translations
    'beaker == 1.5.4',
    'boto == 2.25.0',
    'chameleon == 2.5.3',
    'gevent == 0.13.8',  # Note: gevent 1.0 no longer requires libevent, it bundles libev instead
    'greenlet == 0.3.1',
    'gunicorn == 18.0',
    # 'lingua >= 1.5',  # Only required for generating i18n translations
    'M2Crypto == 0.20.2',
    'pycrypto == 2.0.1',
    'Paste == 1.7.4',
    'pyramid == 1.4',
    'pyramid_beaker == 0.8',
    'pyramid_chameleon == 0.1',
    # 'pyramid_debugtoolbar',  # Optional -- helpful for development/debugging
    'pyramid_layout == 0.8',
    # 'pyramid_mailer >= 0.13',
    # 'pyramid_tm >= 0.7',
    'python-dateutil == 1.4.1',  # Don't use 2.x series unless on Python 3
    'simplejson == 2.0.9',
    # 'SQLAlchemy == 0.8.3',
    # 'waitress >= 0.8.8',  # Pure python WSGI server
    'WTForms == 1.0.2',
]

message_extractors = {'.': [
    ('**.py', 'lingua_python', None),
    ('**.pt', 'lingua_xml', None),
]}

setup(
    name='eucaconsole',
    version='4.0.0',
    description='Eucalyptus Management Console',
    long_description=README + '\n\n' + CHANGES,
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
    message_extractors=message_extractors,
    test_suite="tests",
    entry_points="""\
    [paste.app_factory]
    main = eucaconsole:main
    """,
)
