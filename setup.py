from distutils.core import setup

from setuptools import find_packages

required_packages = [
    'RPi.GPIO',
    'PyYAML'
]

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
