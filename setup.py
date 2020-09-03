#! /usr/bin/env python3

from distutils.core import setup


setup(
    name='hidslcfg',
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='info@homeinfo.de',
    maintainer='Richard Neumann',
    maintainer_email='r.neumann@homeinfo.de',
    requires=['requests'],
    packages=['hidslcfg', 'hidslcfg.cli'],
    scripts=['files/hidslcfg', 'files/hidslreset'],
    description='HOMEINFO Digital Signage Linux configurator.')
