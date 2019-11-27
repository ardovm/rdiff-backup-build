#!/usr/bin/env python3

# This script compiles and bundles together librsync and rdiff-backup

import sys
import platform
import os
import os.path
import shutil
import subprocess
import tarfile
import PyInstaller.__main__

def runCommand(*args):
    """Launch a command and abort if not successful.

    The first parameter must be the executable. Arguments must be
    passed as additional parameters."""
    a = subprocess.call(args)
    if a != 0:
        sys.stderr.write("The command gave an error:\n  %s\n" % " ".join(args))
        sys.exit(1)

if "--help" in sys.argv:
    sys.stderr.write("Usage: %s [version]\n" % sys.argv[0])
    sys.exit(1)
if len(sys.argv) > 1:
    version = sys.argv[1]
else:
    import setuptools_scm
    version = setuptools_scm.get_version(root="rdiff-backup")
# Compilation of librsync
librsyncBinDir = os.path.abspath("librsync-bin")
os.chdir("librsync")
runCommand("cmake", "-DCMAKE_INSTALL_PREFIX=" + librsyncBinDir, ".")
runCommand("cmake", "--build", ".", "--config", "Release")
runCommand("cmake", "--install", ".")# "--config", "Release")
os.chdir("..")
# Build of rdiff-backup
os.chdir("rdiff-backup")
os.putenv("LIBRSYNC_DIR", librsyncBinDir)
runCommand(sys.executable, "setup.py", "build")
os.chdir("build")
strVersion = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
PyInstaller.__main__.run(["--onefile",
                          "--distpath=%s" % os.path.abspath(os.path.join("..", "dist", sys.platform)),
                          "--paths=%s" % os.path.abspath("lib.%s-%s-%s" %
                                                         (sys.platform,
                                                          platform.machine(),
                                                          strVersion)),
                          "--paths=%s" % os.path.join(librsyncBinDir, "bin"),
                          "--paths=%s" % os.path.join(librsyncBinDir, "lib"),
                          "--console", os.path.join("scripts-%s" % strVersion,
                                                    "rdiff-backup")])
os.chdir("..")

# Packaging of rdiff-backup
base="rdiff-backup-%s" % version
with tarfile.open(os.path.join("..", "%s.tar.gz" % base), "w:gz") as z:
    # All files under directory dist
    for f in os.listdir(os.path.join("dist", sys.platform)):
        fWithPath = os.path.join("dist", sys.platform, f)
        if os.path.isfile(fWithPath):
            z.add(fWithPath, os.path.join(base, f))
    # Doc files (list taken from setup.py)
    for f in ['CHANGELOG', 'COPYING', 'README.md',
              os.path.join("docs", "FAQ.md"),
              os.path.join("docs", "examples.md"),
              os.path.join("docs", "DEVELOP.md"),
              os.path.join("docs", "Windows-README.md")]:
        z.add(f, os.path.join(base, f))

