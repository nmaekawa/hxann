#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup
from setuptools import find_packages


project_name='hxann'

def get_version(*file_paths):
    """Retrieves the version from [your_package]/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version(project_name, "__init__.py")


with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'Click>=6.0',
]

test_requirements = [
    'pytest',
    'flake8',
]

setup(
    name=project_name,
    version=version,
    author='nmaekawa',
    author_email='nmaekawa@g.harvard.edu',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="convert csv into video annotation",
    entry_points={
        'console_scripts': [
            '{}={}.cli:main'.format(project_name, project_name),
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    keywords='loris s3resolver ' + project_name,
    long_description=readme,
    packages=find_packages(exclude=['docs', 'tests*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/nmaekawa/{}'.format(project_name),
    zip_safe=False,
)
