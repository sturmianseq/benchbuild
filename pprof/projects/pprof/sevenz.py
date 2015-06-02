#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local


class SevenZip(PprofGroup):

    """ 7Zip """

    class Factory:

        def create(self, exp):
            return SevenZip(exp, "7z", "compression")
    ProjectFactory.addFactory("SevenZip", Factory())

    def run_tests(self, experiment):
        from pprof.project import wrap

        p7z_dir = path.join(self.builddir, self.src_dir)
        exp = wrap(path.join(p7z_dir, "bin", "7za"), experiment)
        exp("b", "-mmt1")

    src_dir = "p7zip_9.38.1"
    src_file = src_dir + "_src_all.tar.bz2"
    src_uri = "http://downloads.sourceforge.net/project/p7zip/p7zip/9.38.1/" + \
        src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar, cp

        p7z_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfj', path.join(self.builddir, self.src_file))
            cp(path.join(p7z_dir, "makefile.linux_clang_amd64_asm"),
               path.join(p7z_dir, "makefile.machine"))

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make, ln
        from pprof.utils.compiler import clang, clang_cxx

        p7z_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(p7z_dir):
            make["CC=" + str(clang()),
                 "CXX=" + str(clang_cxx()),
                 "OPTFLAGS=" + " ".join(self.cflags + self.ldflags),
                 "clean", "all"] & FG

        with local.cwd(self.builddir):
            ln("-sf", path.join(p7z_dir, "bin", "7za"), self.run_f)
