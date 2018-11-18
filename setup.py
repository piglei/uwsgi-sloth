# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
from setuptools import setup, find_packages


# **Python version check**
if sys.version_info < (3, 5):
    error = """
uwsgi-sloth only supports Python 3.5 and above.
When using Python 2.7, please install "uwsgi-sloth<3.0.0" instead.
"""

    print(error, file=sys.stderr)
    sys.exit(1)


setup(
    name='uwsgi-sloth',
    version='3.0.1',
    description='A simple uwsgi access log analyzer',
    long_description=open('README.rst').read(),
    author='piglei',
    author_email='piglei2007@gmail.com',
    url='https://github.com/piglei/uwsgi-sloth',
    keywords='uwsgi log analyzer',
    license='Apache License, Version 2.0',
    packages=find_packages(),
    package_data={"": ['templates/*.html', 'sample.conf']},
    classifiers=[
      "Programming Language :: Python :: 3",
    ],
    install_requires=[
        'jinja2',
        'configobj'
    ],
    scripts=['uwsgi_sloth/uwsgi-sloth']
)
