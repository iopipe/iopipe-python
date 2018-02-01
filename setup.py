from setuptools import find_packages, setup

setup(
    name='iopipe',
    version='1.0.1',
    description='IOpipe agent for serverless Application Performance Monitoring',
    author='IOpipe',
    author_email='support@iopipe.com',
    url='https://github.com/iopipe/iopipe-python',
    packages=find_packages(exclude=('tests', 'tests.*',)),
    extras_require={
        'dev': ['flake8', 'requests'],
    },
    setup_requires=['pytest-runner'],
    tests_require=['mock', 'pytest', 'pytest-benchmark', 'requests'],
    zip_safe=True)
