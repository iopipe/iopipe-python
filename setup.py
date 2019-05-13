import os
import sys

from setuptools import find_packages, setup

try:
    from pypandoc import convert

    README = convert("README.md", "rst")
except (ImportError, OSError):
    README = open(os.path.join(os.path.dirname(__file__), "README.md"), "r").read()

install_requires = []
if sys.version_info[0] == 2:
    install_requires.append("futures")

tests_require = [
    "jmespath>=0.7.1,<1.0.0",
    "mock",
    "more-itertools<6.0.0",
    "pytest==4.1.0",
    "pytest-benchmark==3.2.0",
    "requests",
]

# Lambda doesn't come with sqlite3 support, which is a dependency of pytest-cov, so we
# have to define these dependencies outside the test suite.
coverage_requires = tests_require + ["coverage==5.0a2", "pytest-cov==2.6.1"]

setup(
    name="iopipe",
    version="1.7.18",
    description="IOpipe agent for serverless Application Performance Monitoring",
    long_description=README,
    author="IOpipe",
    author_email="dev@iopipe.com",
    url="https://github.com/iopipe/iopipe-python",
    packages=find_packages(exclude=("tests", "tests.*")),
    extras_require={
        "coverage": coverage_requires,
        "dev": tests_require + ["black==18.6b2", "pre-commit"],
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
