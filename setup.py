#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ibis-api2',
    version='1.99.0',
    description='iBis Api 2',
    long_description=readme,
    author='Raphael Lehmann',
    author_email='kontakt@rleh.de',
    url='https://github.com/iBis-project/server-python',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'falcon',
        'cython',
        'simplejson',
        'SQLAlchemy'
    ]
)
