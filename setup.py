from setuptools import setup

setup(
    name='iopipe',
    version='0.9.2',
    description='IOpipe agent for serverless Application Performance Monitoring',
    author='IOpipe',
    author_email='support@iopipe.com',
    url='https://github.com/iopipe/iopipe-python',
    packages=['iopipe'],
    extras_require={
        'dev': ['flake8', 'requests'],
    },
    setup_requires=['pytest-runner'],
    tests_require=['mock', 'pytest', 'requests'],
    zip_safe=True)
