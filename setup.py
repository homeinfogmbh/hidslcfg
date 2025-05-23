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
        ],
    },
    description="HOMEINFO Digital Signage Linux configurator.",
)
def _post_install():
    from hidslcfg.configure import create_ddbos_start
    from hidslcfg.system import get_system_id,is_ddb_os_system
    if is_ddb_os_system():
        create_ddbos_start(get_system_id())


_post_install()
