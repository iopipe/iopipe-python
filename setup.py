from setuptools import find_packages, setup

setup(
    name='iopipe',
    version='1.2.0',
    description='IOpipe agent for serverless Application Performance Monitoring',
    author='IOpipe',
    author_email='support@iopipe.com',
    url='https://github.com/iopipe/iopipe-python',
    packages=find_packages(exclude=('tests', 'tests.*',)),
    extras_require={
        'dev': ['flake8', 'requests'],
    },
    setup_requires=['pytest-runner'],
    tests_require=['jmespath>=0.7.1,<1.0.0', 'mock', 'pytest', 'pytest-benchmark', 'requests'],
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ])
