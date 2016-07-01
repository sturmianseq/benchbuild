from benchbuild.project import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.settings import CFG

from os import path


class LuleshOMP(BenchBuildGroup):
    """ Lulesh-OMP """

    NAME = 'lulesh-omp'
    DOMAIN = 'scientific'

    def run_tests(self, experiment):
        exp = wrap(self.run_f, experiment)
        for i in range(1, 15):
            run(exp[str(i)])

    src_file = "LULESH_OMP.cc"
    src_uri = "https://codesign.llnl.gov/lulesh/" + src_file

    def download(self):
        Wget(self.src_uri, self.src_file)

    def configure(self):
        pass

    def build(self):
        self.cflags += ["-fopenmp", "-I" + path.join(
            str(CFG["llvm"]["dir"]), "include")]

        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)
        run(clang_cxx["-o", self.run_f, self.src_file])
