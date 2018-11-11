[![Build Status](https://travis-ci.org/chestm007/py_hydropi.svg?branch=master)](https://travis-ci.org/chestm007/py_hydropi)
# py_hydropi

## this program must be ran as root 
nothing malicious happens in this code, but i would advise reading it before 
running just for good measure. 
This is a fairly simple python daemon for controlling hydroponics equipment
via a RaspberryPI. 
All configuration is done via easy to understand YAML files, the example
in `/py_hydropi/defaults/module_config.yaml`
outlines all possible configuration options

## Testing
environment variables: 
`PY_HYDROPI_TESTING=true` 
tests must be ran from the root repository directory

### TODO
- inter-thread events system
- event triggered (ie, turn on fan for 5 mins 1 hour before lights activate)