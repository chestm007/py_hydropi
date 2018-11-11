from distutils.core import setup
import os

from setuptools import find_packages

required_packages = [
    'PyYAML>=3.12',
    'cherrypy>=13.1.0',
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

setup(
    name='py_hydropi',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    description='',
    install_requires=required_packages,
    entry_points="""
        [console_scripts]
        py_hydropi=py_hydropi.main:main
    """
)
