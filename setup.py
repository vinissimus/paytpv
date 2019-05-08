#!/usr/bin/env python

from distutils.core import setup

setup(name='paytpv',
      version='1.0',
      description='Client api SOAP de PayTPV',
      author='Jordi Collell',
      author_email='jordic@vinissimus.com',
      url='https://github.com/vinissimus/paytpv',
      packages=['paytpv'],
      install_requires=[
        'zeep',
      ],
      extras_require={
        'async': [
          'zeep[async]',
          'aiohttp',
        ],
        'test': [
            'pytest',
            'pytest-cov',
            'pytest-flake8',
            'pytest-asyncio',
            'flake8-isort',
          ],
      },
    )
