import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'boto == 2.13.3',
    'pyramid',
    'pyramid_celery',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_deform',
    'pyramid_layout',
    'pyramid_webassets',
    'waitress',
]

setup(
    name='koala',
    version='4.0.0',
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
