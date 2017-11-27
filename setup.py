#!/usr/bin/env python
from pip.req import parse_requirements
from pip.download import PipSession
from setuptools import setup


install_reqs = parse_requirements('./requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]


setup(name='iopipe',
      version='0.8.0',
      description='IOpipe agent for serverless Application Performance Monitoring',
      author='IOpipe',
      author_email='support@iopipe.com',
      url='https://github.com/iopipe/iopipe-python',
      packages=['iopipe'],
      install_requires=reqs,
      extras_require={
          'dev': [
              'flake8'
          ]
      },
      setup_requires=['pytest-runner'],
      tests_require=['pytest']
      )
