"""
gzip experiment within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils import download, run, wrapping
from benchbuild.utils.cmd import tar


class GZip(GentooGroup):
    """
        app-arch/gzip
    """
    NAME = "gzip"
    DOMAIN = "app-arch"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "compression.tar.gz"
    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]

    def compile(self):
        super(GZip, self).compile()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        download.Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def run_tests(self):
        gzip = wrapping.wrap(local.path('/bin/gzip'), self)
        gzip = run.watch(gzip)

        # Compress
        gzip("-f", "-k", "--best", "compression/text.html")
        gzip("-f", "-k", "--best", "compression/chicken.jpg")
        gzip("-f", "-k", "--best", "compression/control")
        gzip("-f", "-k", "--best", "compression/input.source")
        gzip("-f", "-k", "--best", "compression/liberty.jpg")

        # Decompress
        gzip("-f", "-k", "--decompress", "compression/text.html.gz")
        gzip("-f", "-k", "--decompress", "compression/chicken.jpg.gz")
        gzip("-f", "-k", "--decompress", "compression/control.gz")
        gzip("-f", "-k", "--decompress", "compression/input.source.gz")
        gzip("-f", "-k", "--decompress", "compression/liberty.jpg.gz")
