=============================
Eucalyptus Management Console
=============================

The Eucalyptus Management Console is a web-based interface to a local Eucalyptus cloud and/or AWS services.


AWS Services supported
======================

* EC2
* Auto Scaling
* CloudWatch
* IAM


Development environment setup
=============================

Pyramid Setup
-------------
Run `python setup.py develop` to set up the development environment.
This only needs to be run once or when the "requires" package versions in setup.py are modified.

Note: It is strongly recommended to set up the development environment in a virtualenv.

Sass/Compass Setup
------------------
The CSS files are pre-processed using Sass, so you'll need to set up a Sass-to-CSS watcher to output CSS.

To set up Compass as the file watcher...

    sudo gem install compass
    cd koala/static
    compass watch .

Once you have installed compass, there's a handy shortcut to enable the watcher.  From the repo root...

    make watch


Running the management console
==============================
To run the server, you will need to specify the path to the config file (console.ini).
Copy the default ini file to the application root.  At the repo root...

    cp conf/console.default.ini ./console.ini

The default settings assume an SSL environment.  To disable SSL, set session.secure to false in console.ini

    session.secure = false

Run the server with

    ./launcher.sh

`launcher.sh` is provided as an alias for `pserve console.ini`


Running the server in development/debug mode
--------------------------------------------
To have Pyramid automatically detect modifications to templates and views,

1. Change the reload_templates setting to true in console.ini: `pyramid.reload_templates = true`
2. Run the server with the --reload flag: `pserve console.ini --reload`

The `--reload` flag instructs Pyramid to automatically watch for changes in the view callables.

The Pyramid Debug Toolbar can be enabled by adding pyramid_debugtoolbar to the app:main section of console.ini

    [app:main]
    # ...
    pyramid.includes =
        pyramid_beaker
        pyramid_chameleon
        pyramid_debugtoolbar
        pyramid_layout

You may also find it useful to set the logging level to DEBUG in the console.ini config file...

    [logger_root]
    # ...
    handlers = logfile, screen_debug

The management console assumes an SSL setup. To disable SSL for development purposes, set `session.secure = false`
in the config file (console.ini)


Technology Stack
================

Primary Components
------------------
* Pyramid
* Boto
* Zurb Foundation
* AngularJS

Secondary Components
--------------------
* Chameleon (server-side templates)
* pyramid_layout (layout/themes for Pyramid)
* WTForms (server-side forms and validation)
* Beaker and pyramid_beaker (server-side cache/sessions)
* Waitress (WSGI server)

