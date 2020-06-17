from plumbum import local

import benchbuild as bb
from benchbuild.settings import CFG
from benchbuild.utils import download, path
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.settings import get_number_of_jobs


@download.with_wget({
    "2.6.8": 'http://sourceforge.net/'
             'projects/mcrypt/files/MCrypt/2.6.8/mcrypt-2.6.8.tar.gz'
})
class MCrypt(bb.Project):
    """ MCrypt benchmark """

    NAME = 'mcrypt'
    DOMAIN = 'encryption'
    GROUP = 'benchbuild'
    VERSION = '2.6.8'
    SRC_FILE = "mcrypt.tar.gz"

    libmcrypt_dir = "libmcrypt-2.5.8"
    libmcrypt_file = libmcrypt_dir + ".tar.gz"
    libmcrypt_uri = \
        "http://sourceforge.net/projects/mcrypt/files/Libmcrypt/2.5.8/" + \
        libmcrypt_file

    mhash_dir = "mhash-0.9.9.9"
    mhash_file = mhash_dir + ".tar.gz"
    mhash_uri = "http://sourceforge.net/projects/mhash/files/mhash/0.9.9.9/" + \
        mhash_file

    def compile(self):
        self.download()

        download.Wget(self.libmcrypt_uri, self.libmcrypt_file)
        download.Wget(self.mhash_uri, self.mhash_file)

        tar('xfz', self.src_file)
        tar('xfz', self.libmcrypt_file)
        tar('xfz', self.mhash_file)
        builddir = bb.path(self.builddir)
        mcrypt_dir = builddir / "mcrypt-2.6.8"
        mhash_dir = builddir / self.mhash_dir
        libmcrypt_dir = builddir / self.libmcrypt_dir

        _cc = bb.compiler.cc(self)
        _cxx = bb.compiler.cxx(self)
        _make = bb.watch(make)

        # Build mhash dependency
        with bb.cwd(mhash_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)

            with bb.env(CC=_cc, CXX=_cxx):
                _configure("--prefix=" + builddir)
                _make("-j", get_number_of_jobs(CFG), "install")

        # Builder libmcrypt dependency
        with bb.cwd(libmcrypt_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)
            with bb.env(CC=_cc, CXX=_cxx):
                _configure("--prefix=" + builddir)
                _make("-j", CFG["jobs"], "install")

        with bb.cwd(mcrypt_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)
            lib_dir = builddir / "lib"
            inc_dir = builddir / "include"
            env = CFG["env"].value
            mod_env = dict(CC=_cc,
                           CXX=_cxx,
                           LD_LIBRARY_PATH=path.list_to_path(
                               [str(lib_dir)] + env.get("LD_LIBRARY_PATH", [])),
                           LDFLAGS="-L" + str(lib_dir),
                           CFLAGS="-I" + str(inc_dir))
            env.update(mod_env)
            with bb.env(**env):
                _configure("--disable-dependency-tracking", "--disable-shared",
                           "--with-libmcrypt=" + builddir,
                           "--with-libmhash=" + builddir)
            _make("-j", get_number_of_jobs(CFG))

    def run_tests(self):
        mcrypt_dir = bb.path(self.builddir) / "mcrypt-2.6.8"
        mcrypt_libs = mcrypt_dir / "src" / ".libs"

        aestest = bb.wrap(mcrypt_libs / "lt-aestest", self)
        _aestest = bb.watch(aestest)
        _aestest()

        ciphertest = bb.wrap(mcrypt_libs / "lt-ciphertest", self)
        _ciphertest = bb.watch(ciphertest)
        _ciphertest()
