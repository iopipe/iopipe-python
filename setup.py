#!/usr/bin/env python
import re

from pip.req import parse_requirements
from pip.download import PipSession
from setuptools import setup

install_reqs = parse_requirements('./requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]


with open('iopipe/iopipe.py', 'r') as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')


setup(name='iopipe',
      version=version,
      description='IOpipe agent for serverless Application Performance Monitoring',
      author='IOpipe',
      author_email='support@iopipe.com',
      url='https://github.com/iopipe/iopipe-python',
      packages=['iopipe'],
      install_requires=reqs,
      setup_requires=[
          'flake8',
          'pytest-runner'
      ],
      extras_require={
          'dev': [
              'flake8'
          ]
      },
      tests_require=[
          'pytest'
      ]
      )
