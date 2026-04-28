import glob
import logging
import os
import shutil
import subprocess
from aur_python_packer.utils import run_command
from aur_python_packer.sandbox import Sandbox
from aur_python_packer.metadata import MetadataParser

logger = logging.getLogger(__name__)

class Builder:
    """
    Orchestrates the build process of Arch Linux packages.
    Manages environment bootstrapping and sandboxed execution of makepkg.
    """
    def __init__(self, work_dir):
        self.work_dir = os.path.abspath(work_dir)
        self.root_dir = os.path.join(self.work_dir, "root")
        self.sandbox = Sandbox(self.work_dir, self.root_dir)
        self.metadata_parser = MetadataParser()
        self._check_dependencies()

    def _check_dependencies(self):
        """
        Verify that necessary host-system tools are available.
        Required: bubblewrap (bwrap) and unprivileged user namespace support.
        """
        if not shutil.which("bwrap"):
            raise RuntimeError("bubblewrap (bwrap) is required for rootless builds.")

        # Check for unprivileged user namespace support
        try:
            subprocess.run(
                ["unshare", "--user", "true"], check=True, capture_output=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Unprivileged user namespaces are not supported or disabled. "
                "Ensure /proc/sys/kernel/unprivileged_userns_clone is 1 (on some distros) "
                "or your kernel supports them."
            )

    def _bootstrap_root(self, custom_conf, pacman_db_path):
        """
        Initializes a minimal Arch Linux root filesystem within the sandbox
        to ensure build hermeticity.
        """
        # Check if root is already bootstrapped with fakeroot
        if os.path.exists(os.path.join(self.root_dir, "usr/bin/fakeroot")):
            return

        logger.info(
            f"Bootstrapping minimal root at {self.root_dir} (this may take a while)..."
        )
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(os.path.join(self.root_dir, "var/lib/pacman"), exist_ok=True)

        # Copy host's pacman.conf to root to ensure same repositories are available
        # Actually, Manager.build_all uses custom_conf which is based on host's conf.
        # But for other tools in the sandbox, having a good /etc/pacman.conf is helpful.
        host_conf = "/etc/pacman.conf"
        target_conf = os.path.join(self.root_dir, "etc/pacman.conf")
        if os.path.exists(host_conf):
            os.makedirs(os.path.dirname(target_conf), exist_ok=True)
            shutil.copy2(host_conf, target_conf)

        cmd = [
            "pacman", "-Sy",
            "base-devel", "pacman", "python", "git", "bash", "fakeroot",
            "ca-certificates", "ca-certificates-utils", "pacman-contrib",
            "--noconfirm", "--needed",
            "--root", self.root_dir,
            "--config", "/etc/pacman.conf",
        ]
        self.sandbox.run_host_command(cmd, log_level=logging.INFO)

    def _run_in_sandbox(self, cmd, cwd, custom_conf, pacman_db_path, **kwargs):
        """
        Helper to run a command inside the sandbox after generating required shims.
        """
        self.sandbox.generate_shims(custom_conf, pacman_db_path)
        return self.sandbox.run(cmd, cwd, custom_conf, pacman_db_path, **kwargs)

    def build(self, pkgname, directory, deps=None, nocheck=False, custom_conf=None, pacman_db_path=None):
        """
        Main entry point for building a package from a directory containing a PKGBUILD.
        """
        directory = os.path.abspath(directory)
        if not custom_conf:
            raise ValueError("custom_conf is required for rootless builds")

        self._bootstrap_root(custom_conf, pacman_db_path)
        return self.execute_sandboxed_build(
            pkgname, directory, deps, nocheck, custom_conf, pacman_db_path
        )
    
    def execute_sandboxed_build(self, pkgname, directory, deps, nocheck, custom_conf, pacman_db_path):
        """
        Executes makepkg inside the sandbox.
        
        Uses '-s' to automatically install dependencies into the sandbox using 
        the custom pacman configuration.
        """
        logger.info(f"Starting sandboxed build for {pkgname}...")
        cmd = ["makepkg", "-s", "-f", "--noconfirm", "--skippgpcheck"]
        if nocheck:
            cmd.append("--nocheck")

        logger.info(f"Starting sandboxed build for {pkgname}...")
        # Ensure the build user can write to the directory
        # In the sandbox we are root (uid 0), and we mapped our current user to uid 0.
        # So we should have permission.

        # For first-time builds, makepkg -s might fail if repos are not synced.
        # We rely on Manager having done the sync, but inside the sandbox
        # we might need to ensure the DBPath is reachable.
        self._run_in_sandbox(cmd, cwd=directory, custom_conf=custom_conf, pacman_db_path=pacman_db_path)
        logger.info(f"Successfully finished building {pkgname}")
        return self._find_package_file(directory)

    def _find_package_file(self, directory):
        """
        Locates the resulting .pkg.tar.zst file after a successful build.
        """
        pkg_files = glob.glob(os.path.join(directory, "*.pkg.tar.zst"))
        if not pkg_files:
            raise FileNotFoundError(f"Build finished but no package file found in {directory}")
        return max(pkg_files, key=os.path.getmtime)

    def execute_sandboxed_build_info(self, directory, custom_conf, pacman_db_path):
        """
        Executes makepkg --printsrcinfo inside the sandbox to get metadata.
        """
        cmd = ["makepkg", "--printsrcinfo"]
        result = self._run_in_sandbox(
            cmd, cwd=directory, custom_conf=custom_conf, pacman_db_path=pacman_db_path
        )
        return result.stdout
