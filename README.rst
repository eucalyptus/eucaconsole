# Eucalyptus Management Console

The Eucalyptus Management Console is a web-based interface to a local Eucalyptus cloud and/or AWS services.


## AWS Services supported

* Auto Scaling
* EC2
* Elastic Load Balancing (ELB)
* CloudWatch


## Development environment setup

Run `python setup.py develop` to set up the development environment.
This only needs to be run once or when the "requires" package versions in setup.py are modified.

Note: It is strongly recommended the environment be set up in a virtualenv.


## Running the management console

`pserve development.ini` runs the console in development mode, `pserve production.ini` in production mode.

