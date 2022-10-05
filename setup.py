#! /usr/bin/env python3
"""Installation script."""

from setuptools import setup


setup(
    name='hidslcfg',
    setup_requires=['setuptools_scm'],
    python_requires='>=3.10',
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='info@homeinfo.de',
    maintainer='Richard Neumann',
    maintainer_email='r.neumann@homeinfo.de',
    requires=[
        'requests',
        'netifaces',
        'pygobject',
        'pygtk',
        'wgtools'
    ],
    packages=[
        'hidslcfg',
        'hidslcfg.cli',
        'hidslcfg.gui',
        'hidslcfg.openvpn',
        'hidslcfg.wireguard'
    ],
    data_files=[
        ('/usr/share/hidslcfg', [
            'hidslcfg/gui/assets/HI_logo_installer.png',
            'hidslcfg/gui/assets/login.glade',
            'hidslcfg/gui/assets/setup.glade',
            'hidslcfg/gui/assets/installation.glade',
            'hidslcfg/gui/assets/completed.glade'
        ])
    ],
    entry_points={
        'console_scripts': [
            'hidslcfg = hidslcfg.cli.hidslcfg:run',
            'hidslreset = hidslcfg.cli.hidslreset:run',
            'wgmigrate = hidslcfg.cli.wgmigrate:run',
            'hidslcfg-gui = hidslcfg.gui:run'
        ],
    },
    description='HOMEINFO Digital Signage Linux configurator.'
)
