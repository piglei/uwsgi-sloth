# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(name='uwsgi-sloth',
    version='2.0.0',
    description='A simple uwsgi access log analyzer',
    long_description=open('README.rst').read(),
    author='piglei',
    author_email='piglei2007@gmail.com',
    url='https://github.com/piglei/uwsgi-sloth',
    keywords='uwsgi log analyzer',
    license='LICENSE',
    packages=find_packages(),
    package_data={"": ['templates/*.html', 'sample.conf']},
    install_requires=[
        'jinja2',
        'configobj'
    ],
    scripts=['uwsgi_sloth/uwsgi-sloth'])


