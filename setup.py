import os
import sys

from setuptools import find_packages, setup

try:
    from pypandoc import convert

    README = convert("README.md", "rst")
except (ImportError, OSError):
    README = open(os.path.join(os.path.dirname(__file__), "README.md"), "r").read()

install_requires = ["wrapt"]
if sys.version_info[0] == 2:
    install_requires.append("futures")

tests_require = [
    "botocore==1.12.162",
    "fakeredis==1.0.3",
    "jmespath>=0.7.1,<1.0.0",
    "mock",
    "mongomock==3.17.0",
    "more-itertools<6.0.0",
    "mysqlclient==1.4.4",
    "psycopg2-binary==2.8.3",
    "pymongo==3.8.0",
    "PyMySQL==0.9.3",
    "pytest==4.1.0",
    "pytest-benchmark==3.2.0",
    "redis==3.3.4",
    "requests",
]

# Lambda doesn't come with sqlite3 support, which is a dependency of pytest-cov, so we
# have to define these dependencies outside the test suite.
coverage_requires = tests_require + ["coverage==5.0a2", "pytest-cov==2.6.1"]

setup(
    name="iopipe",
    version="1.10.0",
    description="IOpipe agent for serverless Application Performance Monitoring",
    long_description=README,
    author="IOpipe",
    author_email="dev@iopipe.com",
    url="https://github.com/iopipe/iopipe-python",
    packages=find_packages(exclude=("tests", "tests.*")),
    extras_require={
        "coverage": coverage_requires,
        "dev": tests_require + ["black==19.3b0", "pre-commit"],
        "local": install_requires
        + ["botocore==1.12.162", "jmespath>=0.7.1,<1.0.0", "requests"],
    },
    install_requires=install_requires,
    setup_requires=["pytest-runner==4.2"],
    tests_require=tests_require,
    zip_safe=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
