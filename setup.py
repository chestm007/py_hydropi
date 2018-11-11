import time
from distutils.core import setup
import os

from setuptools import find_packages

required_packages = [
    'PyYAML',
    'cherrypy',
    'systemd',
    'pep8',
    'requests'
]

is_rasp_pi = os.uname()[4].startswith('arm')
if is_rasp_pi:
    required_packages.extend([
        'RPi.GPIO',
        'Adafruit_Python_DHT',
        'hcsr04sensor'
    ])

VERSION = os.environ.get('TRAVIS_TAG') or '0.0.0.post{}'.format(int(time.time()))

setup(
    name='py_hydropi',
    version=VERSION,
    url='https://github.com/chestm007/py_hydropi',
    packages=find_packages(),
    author='max',
    author_email='chestm007@hotmail.com',
    license='GPL-2.0',
    requires=required_packages,
    include_package_data=True,
    description='Hydroponics controller for RaspberryPi',
    install_requires=required_packages,
    entry_points="""
        [console_scripts]
        py_hydropi=py_hydropi.main:main
    """
)
