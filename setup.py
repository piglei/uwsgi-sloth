# -*- coding: utf-8 -*-
from setuptools import setup


setup(name='uwsgi-sloth',
    version='1.0.2',
    description='A simple uwsgi access log analyzer',
    long_description=open('README.rst').read(),
    author='piglei',
    author_email='piglei2007@gmail.com',
    url='https://github.com/piglei/uwsgi-sloth',
    keywords='uwsgi log analyzer',
    license='LICENSE',
    packages=['uwsgi_sloth'],
    package_data={"": ['*.html']},
    install_requires=[
        'jinja2',
        'configobj'
    ],
    scripts=['uwsgi_sloth/uwsgi-sloth'])


