import os
import subprocess
import glob

class BuildOrchestrator:
    def __init__(self):
        self.os_type = self.detect_os()

    def detect_os(self):
        if os.path.exists("/etc/arch-release"):
            return "arch"
        if os.path.exists("/etc/manjaro-release"):
            return "manjaro"
        return "unknown"

    def get_os(self):
        return self.os_type

    def build(self, pkgname, directory):
        directory = os.path.abspath(directory)
        if self.os_type == "arch":
            cmd = ['extra-x86_64-build']
        elif self.os_type == "manjaro":
            cmd = ['buildpkg', '-p', pkgname]
        else:
            # Fallback to makepkg (non-chroot) if unknown, though design asks for chroot
            cmd = ['makepkg', '-s', '--noconfirm']

        result = subprocess.run(cmd, cwd=directory, check=True)
        
        # Verify success and find package file
        pkg_files = glob.glob(os.path.join(directory, "*.pkg.tar.zst"))
        if not pkg_files:
            raise FileNotFoundError(f"Build finished but no package file found in {directory}")
        
        return pkg_files[0]
