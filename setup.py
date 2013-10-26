import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'beaker == 1.6.4',
    'boto == 2.15',
    'chameleon == 2.13-1',
    'deform == 2.0a2',
    'pyramid == 1.5a2',
    'pyramid_beaker == 0.8',
    'pyramid_chameleon == 0.1',
    'pyramid_debugtoolbar',
    'pyramid_deform == 0.2',
    'pyramid_layout == 0.8',
    'simplejson == 3.3.1',
    'waitress == 0.8.7',
]

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
    author_email='',
    url='http://www.eucalyptus.com',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="koala",
    entry_points="""\
    [paste.app_factory]
    main = koala:main
    """,
)
