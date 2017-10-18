# Maintainer: Richard Neumann aka rne. <r dot neumann at homeinfo fullstop de>

pkgname='hidsl-cfg'
pkgver='5.2.0'
pkgrel=1
arch=('any')
pkgdesc="HOMEINFO Digital Sigange Linux configuration scripts"
depends=('python' 'python-docopt' 'python-requests' 'tar' 'digital-signage')
license=('GPL3')
groups=('homeinfo')


package() {
    install=${pkgname}.install

    # Install binaries
    install -d -m 755 "${pkgdir}/usr/bin"
    install -m 755 "${srcdir}/hidslcfg" "${pkgdir}/usr/bin"

    # Create symlink "hidslreset"
    cd "${pkgdir}/usr/bin"
    ln -s hidslcfg hidslreset

    # Install sudoers file
    install -d -m 755 "${pkgdir}/etc"
    install -d -m 750 "${pkgdir}/etc/sudoers.d"
    install -m 640 -T "${srcdir}/hidslcfg.sudo" "${pkgdir}/etc/sudoers.d/hidslcfg"

    # Install systemd units
    install -d -m 755 "${pkgdir}/usr/lib/systemd/system"
    install -m 644 "${srcdir}/hidslcfg.target" "${pkgdir}/usr/lib/systemd/system/"
    install -m 644 "${srcdir}/hidslcfg@.service" "${pkgdir}/usr/lib/systemd/system/"

    # Install HOME files
    install -d -m 550 "${pkgdir}/home/hidslcfg"
    install -m 440 -T "${srcdir}/bash_profile" "${pkgdir}/home/hidslcfg/.bash_profile"
}
