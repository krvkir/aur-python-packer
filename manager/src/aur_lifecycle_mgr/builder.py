import os
import subprocess
import glob

class BuildOrchestrator:
    def __init__(self):
        self.os_type = self.detect_os()

    def detect_os(self):
        if os.path.exists("/etc/manjaro-release"):
            return "manjaro"
        if os.path.exists("/etc/arch-release"):
            return "arch"
        return "unknown"

    def get_os(self):
        return self.os_type

    def build(self, pkgname, directory):
        directory = os.path.abspath(directory)
        cmd = None
        if self.os_type == "arch":
            cmd = ['extra-x86_64-build']
        elif self.os_type == "manjaro":
            cmd = ['buildpkg', '-p', pkgname]
        
        # Fallback to makepkg if chroot tools are missing
        if cmd:
            try:
                subprocess.run(['which', cmd[0]], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                print(f"Warning: {cmd[0]} not found, falling back to makepkg")
                cmd = ['makepkg', '-s', '--noconfirm']
        else:
            cmd = ['makepkg', '-s', '--noconfirm']

        result = subprocess.run(cmd, cwd=directory, check=True)
        
        # Verify success and find package file
        pkg_files = glob.glob(os.path.join(directory, "*.pkg.tar.zst"))
        if not pkg_files:
            raise FileNotFoundError(f"Build finished but no package file found in {directory}")
        
        return pkg_files[0]
