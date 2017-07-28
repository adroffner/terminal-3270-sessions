#! /usr/bin/env python

from setuptools import setup
from terminal_3270 import __version__


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='terminal-3270-sessions',
      version=__version__,
      license='PSF Licensed',
      description='IBM 3270 Terminal API Client Sessions',
      long_description=readme(),
      author='Andrew Droffner',
      author_email='ad718x@att.com',
      # url='',
      # download_url='',
      packages=['terminal_3270'],
      install_requires=[
          'py3270>=0.3.4',
      ],
      test_suite='nose.collector',
      tests_require=['nose>=1.3.7'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Python Software Foundation License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.5',
      ])
