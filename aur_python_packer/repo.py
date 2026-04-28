import os
import logging
import glob
import shutil
import subprocess
from aur_python_packer.utils import run_command
from aur_python_packer.config import PacmanConfig

logger = logging.getLogger(__name__)

class RepoManager:
    """
    Manages a local pacman repository of built packages.
    """
    def __init__(self, repo_dir, db_name="localrepo", db_path_override=None, cache_path_override=None, log_path_override=None, gpg_dir_override=None):
        """
        Initializes the repository manager and ensures the local database is initialized.
        """
        self.repo_dir = os.path.abspath(repo_dir)
        self.db_name = db_name
        self.db_path = os.path.join(self.repo_dir, f"{db_name}.db.tar.gz")
        self.config_manager = PacmanConfig(
            repo_dir=self.repo_dir,
            db_name=db_name,
            db_path_override=db_path_override,
            cache_path_override=cache_path_override,
            log_path_override=log_path_override,
            gpg_dir_override=gpg_dir_override
        )

        os.makedirs(self.repo_dir, exist_ok=True)
        if db_path_override: os.makedirs(db_path_override, exist_ok=True)
        if cache_path_override: os.makedirs(cache_path_override, exist_ok=True)
        if log_path_override: os.makedirs(os.path.dirname(log_path_override), exist_ok=True)
        if gpg_dir_override: os.makedirs(gpg_dir_override, exist_ok=True)

        if not os.path.exists(self.db_path):
            logger.info(f"Initializing local repository at {self.repo_dir}")
            run_command(['repo-add', self.db_path])

    def add_package(self, pkg_path):
        """
        Adds a built package (.pkg.tar.zst) to the local repository
        and updates the repository database.
        """
        pkg_name = os.path.basename(pkg_path)
        dest_path = os.path.join(self.repo_dir, pkg_name)
        logger.debug(f"Adding package {pkg_name} to local repository")
        shutil.copy2(pkg_path, dest_path)
        
        # Update repo db
        run_command(['repo-add', self.db_path, dest_path])

    def get_package_files(self):
        """
        Returns a list of all package files present in the repository.
        """
        return glob.glob(os.path.join(self.repo_dir, "*.pkg.tar.zst"))

    def generate_custom_conf(self, base_conf="/etc/pacman.conf", output_path="pacman.conf"):
        """
        Delegates custom pacman.conf generation to the configuration manager.
        """
        return self.config_manager.generate(base_conf, output_path)
