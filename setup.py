#! /usr/bin/env python3
"""Installation script."""

from setuptools import setup


setup(
    name="hidslcfg",
    setup_requires=["setuptools_scm"],
    python_requires=">=3.10",
    author="HOMEINFO - Digitale Informationssysteme GmbH",
    author_email="info@homeinfo.de",
    maintainer="Richard Neumann",
    maintainer_email="r.neumann@homeinfo.de",
    requires=["requests", "netifaces", "pygobject", "pygtk", "wgtools"],
    packages=[
        "hidslcfg",
        "hidslcfg.cli",
        "hidslcfg.gui",
        "hidslcfg.gui.windows",
        "hidslcfg.gui.windows.main",
        "hidslcfg.wireguard",
    ],
    entry_points={
        "console_scripts": [
            "hidslcfg = hidslcfg.cli.hidslcfg:run",
            "hidslreset = hidslcfg.cli.hidslreset:run",
            "hidslcfg-gui = hidslcfg.gui.application:run",
            "hidslcfg-create-index = hidslcfg.configure:create_ddbos_start",
        ],
    },
    description="HOMEINFO Digital Signage Linux configurator.",
)
