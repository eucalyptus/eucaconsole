import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'beaker >= 1.5.4',
    'boto >= 2.25.0',
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
    'pyramid_layout >= 0.8',
    'python-dateutil >= 1.4.1',  # Don't use 2.x series unless on Python 3
    'simplejson >= 2.0.9',
    'WTForms >= 1.0.2',
]

i18n_extras = [
    'Babel',
    'lingua',
]

dev_extras = [
    'pyramid_debugtoolbar',
    'waitress',
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
    extras_require={
        'i18n': i18n_extras,
        'dev': dev_extras,
    },
    message_extractors=message_extractors,
    test_suite="tests",
    entry_points="""\
    [paste.app_factory]
    main = eucaconsole:main
    """,
)
