#!/usr/bin/env python

from distutils.core import setup
import os.path

import versioneer
versioneer.versionfile_source = "circuit/_version.py"
versioneer.versionfile_build = "circuit/_version.py"
versioneer.tag_prefix = ""
versioneer.parentdir_prefix = ""
commands = versioneer.get_cmdclass().copy()

## Get long_description from index.txt:
here = os.path.dirname(os.path.abspath(__file__))
f = open(os.path.join(here, 'README.md'))
long_description = f.read().strip()
f.close()

setup(name='python-circuit',
      version=versioneer.get_version(),
      description='Simple implementation of the Circuit Breaker pattern',
      long_description=long_description,
      author='Johan Rydberg',
      author_email='johan.rydberg@gmail.com',
      url='https://github.com/edgeware/python-circuit',
      packages=['circuit'],
      cmdclass=commands)
