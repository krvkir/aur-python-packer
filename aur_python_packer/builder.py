import glob
import os
import logging
import shutil
import subprocess

from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)

class Builder:
    def __init__(self, work_dir):
        self.work_dir = os.path.abspath(work_dir)
        self.root_dir = os.path.join(self.work_dir, "root")
        self.bin_dir = os.path.join(self.work_dir, "bin")
        self._check_dependencies()

    def _check_dependencies(self):
        if not shutil.which("bwrap"):
            raise RuntimeError("bubblewrap (bwrap) is required for rootless builds.")
        
        # Check for unprivileged user namespace support
        try:
            subprocess.run(["unshare", "--user", "true"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Unprivileged user namespaces are not supported or disabled. "
                "Ensure /proc/sys/kernel/unprivileged_userns_clone is 1 (on some distros) "
                "or your kernel supports them."
            )

    def _bootstrap_root(self, custom_conf):
        if os.path.exists(os.path.join(self.root_dir, "etc/pacman.conf")):
            return

        logger.info(f"Bootstrapping minimal root at {self.root_dir}...")
        os.makedirs(self.root_dir, exist_ok=True)
        
        # Use pacman --root to install base-devel into the directory
        cmd = [
            "pacman", "-Sy", "base-devel", "pacman", "--noconfirm",
            "--root", self.root_dir,
            "--config", custom_conf,
        ]
        run_command(cmd)

    def _generate_sudo_shim(self, custom_conf):
        os.makedirs(self.bin_dir, exist_ok=True)
        shim_path = os.path.join(self.bin_dir, "sudo")
        
        # We want the shim to use the custom pacman.conf
        with open(shim_path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write('if [ "$1" = "pacman" ]; then\n')
            f.write('    shift\n')
            f.write(f'    exec pacman --config "{custom_conf}" "$@"\n')
            f.write('fi\n')
            f.write('exec "$@"\n')
        
        os.chmod(shim_path, 0o755)
        return shim_path

    def _run_in_sandbox(self, cmd, cwd, custom_conf):
        self._generate_sudo_shim(custom_conf)
        
        # bwrap command construction
        bwrap_cmd = [
            "bwrap",
            "--unshare-user",
            "--uid", "0",
            "--gid", "0",
            "--bind", self.root_dir, "/",
            "--dev", "/dev",
            "--proc", "/proc",
            "--tmpfs", "/tmp",
            "--bind", self.work_dir, self.work_dir,
            "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
            "--setenv", "PATH", f"/usr/bin:{self.bin_dir}",
            "--setenv", "HOME", "/root",
            "--chdir", cwd
        ]
        
        # Also bind-mount the directory being built if it's outside work_dir
        if not cwd.startswith(self.work_dir):
             bwrap_cmd.extend(["--bind", cwd, cwd])

        bwrap_cmd.extend(cmd)
        
        run_command(bwrap_cmd, log_level=logging.INFO)

    def build(self, pkgname, directory, deps=None, nocheck=False, custom_conf=None):
        directory = os.path.abspath(directory)
        
        if not custom_conf:
            raise ValueError("custom_conf is required for rootless builds")

        self._bootstrap_root(custom_conf)
        return self.execute_sandboxed_build(pkgname, directory, deps, nocheck, custom_conf)

    def execute_sandboxed_build(self, pkgname, directory, deps, nocheck, custom_conf):
        # Build command for makepkg
        # We use -s to install dependencies, which will use our sudo shim
        cmd = ["makepkg", "-s", "-f", "--noconfirm", "--skippgpcheck"]
        if nocheck:
            cmd.append("--nocheck")

        # Ensure the build user can write to the directory
        # In the sandbox we are root (uid 0), and we mapped our current user to uid 0.
        # So we should have permission.

        self._run_in_sandbox(cmd, cwd=directory, custom_conf=custom_conf)
        return self._find_package_file(directory)

    def _find_package_file(self, directory):
        pkg_files = glob.glob(os.path.join(directory, "*.pkg.tar.zst"))
        if not pkg_files:
            raise FileNotFoundError(
                f"Build finished but no package file found in {directory}"
            )
        return max(pkg_files, key=os.path.getmtime)
