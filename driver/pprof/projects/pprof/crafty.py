#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import cat

class Crafty(PprofGroup):

    """ crafty benchmark """

    class Factory:
        def create(self, exp):
            obj = Crafty(exp, "crafty", "scientific")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Crafty", Factory())

    src_dir = "crafty-23.4"
    src_file = src_dir + ".zip"
    src_uri = "http://www.craftychess.com/crafty-23.4.zip"

    def download(self):
        from plumbum.cmd import wget, unzip

        book_bin = "http://www.craftychess.com/book.bin"
        with local.cwd(self.builddir):
            wget(self.src_uri)
            wget(book_bin)
            unzip(path.join(self.builddir, self.src_file))

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make, ln

        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")
        clang = local[path.join(llvm, "clang")]
        crafty_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(crafty_dir):
            target_cflags = self.cflags
            target_cxflags = [] 
            target_ldflags = self.ldflags
            target_opts = ["-DINLINE64", "-DCPUS=1"]

            make["target=LINUX",
                 "CC=" + str(clang),
                 "CFLAGS=" + " ".join(target_cflags),
                 "CXFLAGS=" + " ".join(target_cxflags),
                 "LDFLAGS=" + " ".join(target_ldflags),
                 "opt=" + " ".join(target_opts),
                 "crafty-make"] & FG

        with local.cwd(self.builddir):
            ln("-sf", path.join(crafty_dir, "crafty"), self.run_f)

    def run(self, experiment):
        with local.cwd(self.builddir):
            (cat[path.join(self.testdir, "test1.sh")] | experiment) & FG
            (cat[path.join(self.testdir, "test2.sh")] | experiment) & FG

