#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import (ProjectFactory, log_with, log)
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import ln


class Ccrypt(PprofGroup):

    """ ccrypt benchmark """

    check_f = "check"

    class Factory:

        def create(self, exp):
            obj = Ccrypt(exp, "ccrypt", "encryption")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Ccrypt", Factory())

    def prepare(self):
        super(Ccrypt, self).prepare()
        check_f = path.join(self.testdir, self.check_f)
        ln("-s", check_f, path.join(self.builddir, self.check_f))

    def clean(self):
        check_f = path.join(self.builddir, self.check_f)
        self.products.add(check_f)

        super(Ccrypt, self).clean()

    src_dir = "ccrypt-1.10"
    src_file = "ccrypt-1.10.tar.gz"
    src_uri = "http://ccrypt.sourceforge.net/download/ccrypt-1.10.tar.gz"

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar, cp

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))

    def configure(self):
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        ccrypt_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(ccrypt_dir):
            configure = local[path.join(ccrypt_dir, "configure")]

            with local.env(CC=str(lt_clang(self.cflags)),
                           CXX=str(lt_clang_cxx(self.cflags)),
                           LDFLAGS=" ".join(self.ldflags)):
                configure & FG

    def build(self):
        from plumbum.cmd import make, mv, rm

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            sh_file = path.join("src", "ccrypt")
            rm("-f", sh_file)
            make & FG
            mv(sh_file, self.bin_f)
        self.run_f = self.bin_f

    def run_tests(self, experiment):
        from plumbum.cmd import make, chmod

        exp = experiment(self.run_f)

        ccrypt_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ccrypt_dir):
            sh_file = path.join("src", self.name)
            with open(sh_file, 'w') as ccrypt:
                ccrypt.write("#!/usr/bin/env bash\n")
                ccrypt.write("exec " + str(exp["\"$@\""]))
            chmod("+x", sh_file)
            make["check"] & FG