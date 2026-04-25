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

    def build(self, pkgname, directory, nocheck=False, custom_conf=None):
        directory = os.path.abspath(directory)
        cmd = None
        env = os.environ.copy()

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
                cmd = ['makepkg', '-s', '-f', '--noconfirm', '--skippgpcheck']
        else:
            cmd = ['makepkg', '-s', '-f', '--noconfirm', '--skippgpcheck']

        if nocheck and 'makepkg' in cmd[0]:
            cmd.append('--nocheck')

        if custom_conf and 'makepkg' in cmd[0]:
            # Create a wrapper script for pacman to use the custom config
            wrapper_dir = os.path.join(os.getcwd(), "work", "bin")
            wrapper_path = os.path.join(wrapper_dir, "pacman")
            with open(wrapper_path, 'w') as f:
                f.write(f'#!/bin/bash\n/usr/bin/pacman --config "{custom_conf}" "$@"\n')
            os.chmod(wrapper_path, 0o755)
            env['PATH'] = wrapper_dir + os.pathsep + env['PATH']

        result = subprocess.run(cmd, cwd=directory, check=True, env=env)
        
        # Verify success and find package file
        pkg_files = glob.glob(os.path.join(directory, "*.pkg.tar.zst"))
        if not pkg_files:
            raise FileNotFoundError(f"Build finished but no package file found in {directory}")
        
        return pkg_files[0]
