import os
import logging
import glob
import shutil
import subprocess

from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)

class RepoManager:
    def __init__(self, repo_dir, db_name="localrepo", db_path_override=None, cache_path_override=None, log_path_override=None, gpg_dir_override=None):
        self.repo_dir = os.path.abspath(repo_dir)
        self.db_name = db_name
        self.db_path = os.path.join(self.repo_dir, f"{db_name}.db.tar.gz")
        self.db_path_override = db_path_override
        self.cache_path_override = cache_path_override
        self.log_path_override = log_path_override
        self.gpg_dir_override = gpg_dir_override

        os.makedirs(self.repo_dir, exist_ok=True)
        if self.db_path_override:
            os.makedirs(self.db_path_override, exist_ok=True)
        if self.cache_path_override:
            os.makedirs(self.cache_path_override, exist_ok=True)

        if not os.path.exists(self.db_path):
            logger.info(f"Initializing local repository at {self.repo_dir}")
            run_command(['repo-add', self.db_path])

    def add_package(self, pkg_path):
        pkg_name = os.path.basename(pkg_path)
        dest_path = os.path.join(self.repo_dir, pkg_name)
        logger.debug(f"Adding package {pkg_name} to local repository")
        shutil.copy2(pkg_path, dest_path)
        
        # Update repo db
        run_command(['repo-add', self.db_path, dest_path])

    def get_package_files(self):
        return glob.glob(os.path.join(self.repo_dir, "*.pkg.tar.zst"))

    def get_pacman_conf_fragment(self):
        return f"""
[{self.db_name}]
SigLevel = Optional TrustAll
Server = file://{self.repo_dir}
"""

    def generate_custom_conf(self, base_conf="/etc/pacman.conf", output_path="pacman.conf"):
        with open(base_conf, 'r') as f:
            content = f.read()
        
        # Remove existing DBPath and CacheDir lines
        new_lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("DBPath") or stripped.startswith("CacheDir"):
                continue
            # Also remove [options] header, we will add it back at the top
            if stripped == "[options]":
                continue
            new_lines.append(line)

        # Re-insert our overrides under a fresh [options] header
        overrides = ["[options]"]
        if self.db_path_override:
            overrides.append(f"DBPath = {self.db_path_override}")
        
        if self.cache_path_override:
            overrides.append(f"CacheDir = {self.cache_path_override}")

        if self.log_path_override:
            overrides.append(f"LogFile = {self.log_path_override}")

        if self.gpg_dir_override:
            overrides.append(f"GPGDir = {self.gpg_dir_override}")

        with open(output_path, 'w') as f:
            f.write("\n".join(overrides) + "\n")
            f.write("\n".join(new_lines) + "\n")
            f.write(self.get_pacman_conf_fragment())
        return os.path.abspath(output_path)
