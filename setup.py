# -*- coding: utf-8 -*-
from distutils.core import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='uwsgi-sloth',
      version='1.0.0',
      description='A simple uwsgi access log analyzer',
      long_description=readme(),
      author='piglei',
      author_email='piglei2007@gmail.com',
      url='https://github.com/piglei/uwsgi-sloth',
      keywords='uwsgi log analyzer',
      license='LICENSE',
      packages=['uwsgi_sloth'],
      install_requires=[
          'jinja2',
      ],
      scripts=['uwsgi_sloth/uwsgi-sloth'])


