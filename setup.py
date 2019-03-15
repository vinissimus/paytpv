#!/usr/bin/env python

from distutils.core import setup

setup(name='paytpv',
      version='1.0',
      description='Client api SOAP de PayTPV',
      author='Iskra',
      author_email='a.llusa@iskra.cat',
      url='https://iskra.cat',
      packages=['paytpv'],
      install_requires=[
        'zeep',
        ],
      extras_require={
        'test': [
            'pytest',
            'pytest-cov',
            'pytest-flake8',
            'flake8-isort',
          ],
      },
     )
