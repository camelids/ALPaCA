#!/usr/bin/env python

from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session='hack')
reqs = [str(ir.req) for ir in install_reqs]

setup(name='ALPaCA',
      version='0.2.0',
      description='A server-side website fingerprinting defense',
      author='camelids',
      url='https://github.com/camelids/ALPaCA/tree/strings',
      packages=['alpaca', 'alpaca.dists'],
      install_requires=reqs,
     )
