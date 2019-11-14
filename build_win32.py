#!/usr/bin/env python

# This script compiles and bundles together librsync and rdiff-backup

import sys
import os
import os.path
import subprocess
import zipfile
import win32api
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
    sys.path.append(os.path.abspath(os.path.join(".", "rdiff-backup", "src")))
    from rdiff_backup.Version import version
# Compilation of librsync
librsyncBinDir = os.path.abspath("librsync-bin")
os.chdir("librsync")
runCommand("cmake", "-DCMAKE_INSTALL_PREFIX=" + librsyncBinDir, "-A", "Win32",
           ".")
runCommand("cmake", "--build", ".", "--config", "Release")
runCommand("cmake", "--install", ".", "--config", "Release")
os.chdir("..")
# Build of rdiff-backup
os.chdir("rdiff-backup")
runCommand(sys.executable, os.path.join(".", "tools", "makedist"), "--no-tar",
           version)
os.chdir("rdiff-backup-%s" % version)
if "VS160COMNTOOLS" not in os.environ:
    sys.stderr.write("VS160COMNTOOLS environment variable not set.\n")
    sys.exit(1)
os.putenv("LIBRSYNC_DIR", librsyncBinDir)
runCommand(sys.executable, "setup.py", "build")
os.chdir("build")
PyInstaller.__main__.run(["--onefile",
                          "--distpath=%s" % os.path.abspath(os.path.join("..", "dist", "win32")),
                          "--paths=%s" % os.path.abspath("lib.win32-3.7"),
                          "--paths=%s" % os.path.join(librsyncBinDir, "bin"),
                          "--paths=%s" % os.path.join(librsyncBinDir, "lib"),
                          "--console", os.path.join("scripts-3.7", "rdiff-backup")])
os.chdir("..")

# Packaging of rdiff-backup
with zipfile.ZipFile(os.path.join("..", "..",
                                  "rdiff-backup-%s.zip" % version), "w",
                     zipfile.ZIP_DEFLATED) as z:
    # All files under directory dist
    for f in os.listdir(os.path.join("dist", "win32")):
        fWithPath = os.path.join("dist", "win32", f)
        if os.path.isfile(fWithPath):
            z.write(fWithPath, f)
    # Doc files (list taken from setup.py)
    for f in ['CHANGELOG', 'COPYING', 'README.md', 'FAQ.md', 'examples.md', 'DEVELOP.md']:
        z.write(f, f)
