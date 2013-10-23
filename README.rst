*****************************
Eucalyptus Management Console
*****************************

The Eucalyptus Management Console is a web-based interface to a local Eucalyptus cloud and/or AWS services.


AWS Services supported
======================

* Auto Scaling
* EC2
* Elastic Load Balancing (ELB)
* CloudWatch


Development environment setup
=============================

Pyramid Setup
^^^^^^^^^^^^^
Run `python setup.py develop` to set up the development environment.
This only needs to be run once or when the "requires" package versions in setup.py are modified.

Note: It is strongly recommended the environment be set up in a virtualenv.

Sass/Compass Setup
^^^^^^^^^^^^^^^^^^
The CSS files are pre-processed using Sass, so you'll need to set up a Sass-to-CSS watcher to output CSS.

To set up Compass as the file watcher...

    sudo gem install compass
    cd koala/static
    compass watch .


Running the management console
==============================

`pserve development.ini` runs the console in development mode, `pserve production.ini` in production mode.

`launcher.sh` is provided as an alias for `pserve production.ini`

To have Pyramid automatically detect modifications, use `pserve development.ini --reload`



