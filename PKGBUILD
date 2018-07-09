# Maintainer: Richard Neumann aka rne. <r dot neumann at homeinfo fullstop de>

pkgname='hidslcfg'
pkgver='8.2.0'
pkgrel=1
arch=('any')
pkgdesc="HOMEINFO Digital Sigange Linux configuration scripts"
depends=('python' 'python-docopt' 'python-requests' 'tar' 'digital-signage')
license=('GPL3')
groups=('homeinfo')


package() {
    # Install python stuff.
    # This also installs the scripts.
    python setup.py install --root="${pkgdir}" --optimize=1

    # Install sudoers file.
    install -d -m 755 "${pkgdir}/etc"
    install -d -m 750 "${pkgdir}/etc/sudoers.d"
    install -m 640 -T "${srcdir}/files/hidslcfg.sudo" "${pkgdir}/etc/sudoers.d/hidslcfg"

    # Install systemd units.
    install -d -m 755 "${pkgdir}/usr/lib/systemd/system"
    install -m 644 "${srcdir}/files/hidslcfg.target" "${pkgdir}/usr/lib/systemd/system/"
    install -m 644 "${srcdir}/files/hidslcfg@.service" "${pkgdir}/usr/lib/systemd/system/"

    # Install HOME files.
    install -d -m 550 "${pkgdir}/home/hidslcfg"
    install -m 440 -T "${srcdir}/files/bash_profile" "${pkgdir}/home/hidslcfg/.bash_profile"

    # Install sysusers configuration.
    install -d -m 755 "${pkgdir}/usr/lib/sysusers.d"
    install -m 644 "${srcdir}/hidslcfg.conf" "${pkgdir}/usr/lib/sysusers.d/"
}
