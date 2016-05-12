#! /usr/bin/env python3
#
#  HIDSL installation script
#
############################

from subprocess import run


class Command():

    def __init__(self, command, *args):
        self.command = command
        self.args = args

    def __call__(self, *pkgs):
        return run(self)

    def __str__(self):
        return ' '.join(self)

    def __iter__(self):
        yield self.command
        yield from self.args


class Pacstrap(Command):

    def __init__(self, dst, *pkgs):
        super().__init__(...)
        sel


class ArchChroot():

    def __init__(self, *args):
        super().__init__('/usr/bin/arch-chroot', *args)
