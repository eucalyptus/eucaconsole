import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'Babel == 1.3',
    'beaker == 1.6.4',
    'boto == 2.17.0',
    'chameleon == 2.13-1',
    'gevent == 0.13.8',  # Requires libevent
    'greenlet == 0.4.1',
    'gunicorn == 18.0',
    'lingua == 1.5',
    'M2Crypto == 0.21.1',
    'ordereddict == 1.1',  # Required by Chameleon for Python 2.6 compatibility
    'pycrypto == 2.6.1',
    'pyramid == 1.5a2',
    'pyramid_beaker == 0.8',
    'pyramid_chameleon == 0.1',
    'pyramid_debugtoolbar',  # Optional -- helpful for development/debugging
    'pyramid_layout == 0.8',
    'pyramid_mailer == 0.13',
    'pyramid_tm == 0.7',
    'simplejson == 3.3.1',
    'SQLAlchemy == 0.8.3',
    'waitress == 0.8.7',
    'WTForms == 1.0.5',
]

message_extractors = {'.': [
    ('**.py', 'lingua_python', None),
    ('**.pt', 'lingua_xml', None),
]}

setup(
    name='koala',
    version='4.0.0-prealpha',
    description='Koala, the Eucalyptus Management Console',
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
    tests_require=requires,
    message_extractors=message_extractors,
    test_suite="koala",
    entry_points="""\
    [paste.app_factory]
    main = koala:main
    """,
)
