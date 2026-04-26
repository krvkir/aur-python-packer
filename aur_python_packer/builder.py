import os
import subprocess
import glob
import shutil

class Builder:
    def __init__(self, local_only=False):
        self.os_type = self.detect_os()
        self.local_only = local_only

    def detect_os(self):
        if os.path.exists("/etc/manjaro-release"):
            return "manjaro"
        if os.path.exists("/etc/arch-release"):
            return "arch"
        return "unknown"

    def check_chroot_tools(self):
        if self.os_type == "arch":
            tool = "extra-x86_64-build"
            if shutil.which(tool):
                return tool
        elif self.os_type == "manjaro":
            for tool in ["chrootbuild", "buildpkg"]:
                if shutil.which(tool):
                    return tool

        return None

    def build(self, pkgname, directory, nocheck=False, custom_conf=None):
        directory = os.path.abspath(directory)

        if self.local_only:
            return self.execute_local_build(pkgname, directory, nocheck, custom_conf)
        
        chroot_tool = self.check_chroot_tools()
        if chroot_tool:
            return self.execute_chroot_build(chroot_tool, pkgname, directory, nocheck, custom_conf)
        
        raise RuntimeError(
            f"Chroot build tools not found for OS type '{self.os_type}'. "
            "Install 'devtools' (Arch) or 'manjaro-tools-pkg' (Manjaro), "
            "or use --local to build on the host system."
        )

    def execute_chroot_build(self, tool, pkgname, directory, nocheck, custom_conf):
        cmd = [tool]
        if tool in ["chrootbuild", "buildpkg"]:
            cmd.extend(["-p", pkgname])
        
        # TODO: Handle custom_conf for chroot tools if needed
        subprocess.run(cmd, cwd=directory, check=True)
        return self._find_package_file(directory)

    def execute_local_build(self, pkgname, directory, nocheck, custom_conf):
        cmd = ['makepkg', '-s', '-f', '--noconfirm', '--skippgpcheck']
        if nocheck:
            cmd.append('--nocheck')

        env = os.environ.copy()
        if custom_conf:
            wrapper_dir = os.path.join(os.path.dirname(custom_conf), "bin")
            os.makedirs(wrapper_dir, exist_ok=True)
            wrapper_path = os.path.join(wrapper_dir, "pacman")
            with open(wrapper_path, 'w') as f:
                f.write(f'#!/bin/bash\n/usr/bin/pacman --config "{custom_conf}" "$@"\n')
            os.chmod(wrapper_path, 0o755)
            env['PATH'] = wrapper_dir + os.pathsep + env['PATH']

        subprocess.run(cmd, cwd=directory, check=True, env=env)
        return self._find_package_file(directory)

    def _find_package_file(self, directory):
        pkg_files = glob.glob(os.path.join(directory, "*.pkg.tar.zst"))
        if not pkg_files:
            raise FileNotFoundError(f"Build finished but no package file found in {directory}")
        return max(pkg_files, key=os.path.getmtime)
