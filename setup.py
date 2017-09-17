#!/usr/bin/env python
import os
from setuptools import setup


BASE = os.path.dirname(__file__)
README_PATH = os.path.join(BASE, 'README.rst')
CHANGES_PATH = os.path.join(BASE, 'CHANGES.rst')
long_description = '\n\n'.join((
    open(README_PATH).read(),
    open(CHANGES_PATH).read(),
))


setup(
    name='django-allauth-extras',
    version='0.0.2',
    url='https://github.com/damoti/django-allauth-extras',
    license='BSD',
    description='Various extras for django-allauth package.',
    long_description=long_description,
    author='Lex Berezhny',
    author_email='lex@damoti.com',
    keywords='django,auth,authentication,admin',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['allauth_extras'],
)
