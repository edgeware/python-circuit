#!/usr/bin/env python
from setuptools import setup


import versioneer
versioneer.versionfile_source = "circuit/_version.py"
versioneer.versionfile_build = "circuit/_version.py"
versioneer.tag_prefix = ""
versioneer.parentdir_prefix = ""
commands = versioneer.get_cmdclass().copy()

with open('README.md') as f:
    long_description = f.read().strip()

setup(name='python-circuit',
      version=versioneer.get_version(),
      description='Simple implementation of the Circuit Breaker pattern',
      long_description=long_description,
      author='Edgeware',
      author_email='info@edgeware.tv',
      url='https://github.com/edgeware/python-circuit',
      packages=['circuit'],
      test_suite='circuit.test',
      tests_require=[
          'mockito==0.5.2',
          'Twisted>=10.2'
      ],
      cmdclass=commands)
