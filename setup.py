#! /usr/bin/env python3
"""Installation script."""

from setuptools import setup


setup(
    name='hidslcfg',
    setup_requires=['setuptools_scm'],
    python_requires='>=3.8',
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='info@homeinfo.de',
    maintainer='Richard Neumann',
    maintainer_email='r.neumann@homeinfo.de',
    requires=['requests', 'netifaces', 'wgtools'],
    packages=['hidslcfg', 'hidslcfg.cli'],
    entry_points={
        'console_scripts': [
            'hidslcfg = hidslcfg:cli:hidslcfg:run',
            'hidslreset = hidslcfg:cli:hidslreset:run',
            'wgmigrate = hidslcfg:cli:wgmigrate:run'
        ],
    },
    description='HOMEINFO Digital Signage Linux configurator.'
)
