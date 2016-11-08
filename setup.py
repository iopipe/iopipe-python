#!/usr/bin/env python

from pip.req import parse_requirements
from pip.download import PipSession
from setuptools import setup

install_reqs = parse_requirements('./requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(name='iopipe',
      version='0.1.3',
      description='IOpipe Collector for serverless Application Performance Monitoring',
      author='Eric Windisch',
      author_email='eric@iopipe.com',
      url='https://github.com/iopipe/iopipe-python',
      packages=['iopipe'],
      install_requires=reqs,
      setup_requires=[
          "flake8"
      ],
      extras_require={
          'dev': [
              'flake8'
          ]
      }
     )
