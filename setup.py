#!/usr/bin/env python
import sys

from setuptools import setup

with open('README.md') as f:
    long_description = f.read().strip()

tests_require = [
    'mockito==0.6.0',
    'Twisted>=10.2'
]

if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup(name='python-circuit',
      version='0.1.8',
      description='Simple implementation of the Circuit Breaker pattern',
      long_description=long_description,
      author='Edgeware',
      author_email='info@edgeware.tv',
      url='https://github.com/edgeware/python-circuit',
      license='Apache v2.0 License',
      packages=['circuit'],
      test_suite='circuit.test',
      tests_require=tests_require)
