from benchbuild.project import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run

from plumbum import local
from benchbuild.utils.cmd import make, mkdir, tar

from os import path


class TCC(BenchBuildGroup):
    NAME = 'tcc'
    DOMAIN = 'compilation'
    VERSION = '0.9.26'

    src_dir = "tcc-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.bz2"
    src_uri = "http://download-mirror.savannah.gnu.org/releases/tinycc/" + \
       SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xjf", self.SRC_FILE)

    def configure(self):
        mkdir("build")
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        with local.cwd("build"):
            configure = local[path.join(self.src_dir, "configure")]
            run(configure["--cc=" + str(clang), "--libdir=/usr/lib64"])

    def build(self):
        with local.cwd("build"):
            run(make)

    def run_tests(self, experiment):
        wrap(self.run_f, experiment)
        run(make["test"])
