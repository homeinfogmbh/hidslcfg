# Maintainer: Richard Neumann aka rne. <r dot neumann at homeinfo fullstop de>

pkgname=('hidsl-cfg' 'hidsl-setup')
pkgver='1.0.0'
pkgrel=1
arch=('any')
license=('GPL3')
groups=('homeinfo')
pkgdir='pkg'
srcdir='src'


package_hidsl-cfg() {
    pkgdesc="HOMEINFO Digital Sigange Linux setup and configuration scripts"
    depends=('python' 'python-requests' 'sudo' 'tar')
    install=${pkgname}.install

    # Install binaries
    install -d -m 755 "${pkgdir}/usr/bin
    install -m 755 "${srcdir}/hidslcfg" "${pkgdir}/usr/bin"

    # Install sudoers file
    install -d -m 755 "${pkgdir}/etc"
    install -d -m 750 "${pkgdir}/etc/sudoers.d"
    install -m 640 -T "${srcdir}/hidslcfg.sudo" "${pkgdir}/etc/sudoers.d/hidslcfg"

    # Install systemd units
    install -d -m 755 "${pkgdir}/usr/lib/systemd/system"
    install -m 644 "${srcdir}/hidslcfg.service" "${pkgdir}/usr/lib/systemd/system/"
    install -m 644 "${srcdir}/hidslcfg.target" "${pkgdir}/usr/lib/systemd/system/"
}

package_hidsl-setup() {
    pkgdesc="HOMEINFO Digital Sigange Linux setup scripts"

    # TODO: implement
}
