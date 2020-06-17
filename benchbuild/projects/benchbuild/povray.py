from plumbum import FG, local

import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import (cp, find, grep, head, make, mkdir, sed, sh,
                                  tar)


@download.with_git('https://github.com/POV-Ray/povray', limit=5)
class Povray(bb.Project):
    """ povray benchmark """

    NAME = 'povray'
    DOMAIN = 'multimedia'
    GROUP = 'benchbuild'
    SRC_FILE = 'povray.git'
    VERSION = 'HEAD'

    boost_src_dir = "boost_1_59_0"
    boost_src_file = boost_src_dir + ".tar.bz2"
    boost_src_uri = \
        "http://sourceforge.net/projects/boost/files/boost/1.59.0/" + \
        boost_src_file

    def compile(self):
        self.download()
        download.Wget(self.boost_src_uri, self.boost_src_file)
        tar("xfj", self.boost_src_file)

        cp("-ar", bb.path(self.testdir) / "cfg", '.')
        cp("-ar", bb.path(self.testdir) / "etc", '.')
        cp("-ar", bb.path(self.testdir) / "scenes", '.')
        cp("-ar", bb.path(self.testdir) / "share", '.')
        cp("-ar", bb.path(self.testdir) / "test", '.')

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        # First we have to prepare boost for lady povray...
        boost_prefix = "boost-install"
        with bb.cwd(self.boost_src_dir):
            mkdir(boost_prefix)
            bootstrap = local["./bootstrap.sh"]
            _bootstrap = bb.watch(bootstrap)
            _bootstrap("--with-toolset=clang",
                       "--prefix=\"{0}\"".format(boost_prefix))

            _b2 = bb.watch(local["./b2"])
            _b2("--ignore-site-config", "variant=release", "link=static",
                "threading=multi", "optimization=speed", "install")

        src_file = bb.path(self.src_file)
        with bb.cwd(src_file):
            with bb.cwd("unix"):
                sh("prebuild.sh")

            configure = local["./configure"]
            _configure = bb.watch(configure)
            with bb.env(COMPILED_BY="BB <no@mail.nono>",
                        CC=str(clang),
                        CXX=str(clang_cxx)):
                _configure("--with-boost=" + boost_prefix)
            _make = bb.watch(make)
            _make("all")

    def run_tests(self):
        povray_binary = bb.path(self.src_file) / "unix" / self.name
        tmpdir = bb.path("tmp")
        tmpdir.mkdir()

        povini = bb.path("cfg") / ".povray" / "3.6" / "povray.ini"
        scene_dir = bb.path("share") / "povray-3.6" / "scenes"

        povray = bb.wrap(povray_binary, self)
        _povray = bb.watch(povray)
        pov_files = find(scene_dir, "-name", "*.pov").splitlines()
        for pov_f in pov_files:
            with bb.env(POVRAY=povray_binary,
                        INSTALL_DIR='.',
                        OUTPUT_DIR=tmpdir,
                        POVINI=povini):
                options = ((((head["-n", "50", "\"" + pov_f + "\""] |
                              grep["-E", "'^//[ ]+[-+]{1}[^ -]'"]) |
                             head["-n", "1"]) | sed["s?^//[ ]*??"]) & FG)
                _povray("+L" + scene_dir,
                        "+L" + tmpdir,
                        "-i" + pov_f,
                        "-o" + tmpdir,
                        options,
                        "-p",
                        retcode=None)
