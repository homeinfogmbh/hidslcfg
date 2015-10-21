#! /usr/bin/env python3

from distutils.core import setup

setup(
    name='hidslcfg',
    author='Richard Neumann',
    author_email='r.neumann@homeinfo.de',
    requires=['docopt', 'requests'],
    py_modules=['hidslcfg.py'],
    license=open('LICENSE').read()
)
