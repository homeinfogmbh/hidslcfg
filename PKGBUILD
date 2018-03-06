# Maintainer: Richard Neumann aka rne. <r dot neumann at homeinfo fullstop de>

pkgname='hidslcfg'
pkgver='7.2.9'
pkgrel=1
arch=('any')
pkgdesc="HOMEINFO Digital Sigange Linux configuration scripts"
depends=('python' 'python-docopt' 'python-requests' 'tar' 'digital-signage')
license=('GPL3')
groups=('homeinfo')
provides=('hidsl-cfg')
replaces=('hidsl-cfg')


package() {
    # Install binaries.
    install -d -m 755 "${pkgdir}/usr/bin"
    install -m 755 "${srcdir}/hidslcfg" "${pkgdir}/usr/bin"

    # Create symlink "hidslreset".
    cd "${pkgdir}/usr/bin"
    ln -s hidslcfg hidslreset

    # Install sudoers file.
    install -d -m 755 "${pkgdir}/etc"
    install -d -m 750 "${pkgdir}/etc/sudoers.d"
    install -m 640 -T "${srcdir}/hidslcfg.sudo" "${pkgdir}/etc/sudoers.d/hidslcfg"

    # Install systemd units.
    install -d -m 755 "${pkgdir}/usr/lib/systemd/system"
    install -m 644 "${srcdir}/hidslcfg.target" "${pkgdir}/usr/lib/systemd/system/"
    install -m 644 "${srcdir}/hidslcfg@.service" "${pkgdir}/usr/lib/systemd/system/"

    # Install HOME files.
    install -d -m 550 "${pkgdir}/home/hidslcfg"
    install -m 440 -T "${srcdir}/bash_profile" "${pkgdir}/home/hidslcfg/.bash_profile"

    # Install ALPM hooks.
    install -d -m 755 "${pkgdir}/usr/share/libalpm/hooks"
    install -m 644 "${srcdir}/hidslcfg-01-useradd.hook" "${pkgdir}/usr/share/libalpm/hooks/"
    install -m 644 "${srcdir}/hidslcfg-02-chown-home.hook" "${pkgdir}/usr/share/libalpm/hooks/"
}
