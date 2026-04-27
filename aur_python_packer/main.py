import os
import logging
import subprocess

from aur_python_packer.builder import Builder
from aur_python_packer.generator import PyPIGenerator, generate_srcinfo
from aur_python_packer.repo import RepoManager
from aur_python_packer.resolver import DependencyResolver, clone_aur_repo
from aur_python_packer.state import StateManager
from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)

class Manager:
    def __init__(self, work_dir="work"):
        self.work_dir = os.path.abspath(work_dir)
        os.makedirs(self.work_dir, exist_ok=True)

        self.state_file = os.path.join(self.work_dir, "build_index.json")
        self.repo_dir = os.path.join(self.work_dir, "local_repo")
        self.aur_cache_dir = os.path.join(self.work_dir, "aur_cache")
        # self.generated_dir = os.path.join(self.work_dir, "generated")
        self.generated_dir = self.work_dir
        self.pacman_conf_path = os.path.join(self.work_dir, "pacman.conf")
        self.pacman_db_path = os.path.join(self.work_dir, "pacman_db")
        self.pacman_cache_path = os.path.join(self.work_dir, "pacman_cache")
        self.pacman_log_path = os.path.join(self.work_dir, "pacman.log")
        self.gpg_dir = os.path.join(self.work_dir, "gnupg")

        self.state = StateManager(self.state_file)
        self.repo = RepoManager(
            self.repo_dir,
            db_path_override=self.pacman_db_path,
            cache_path_override=self.pacman_cache_path,
            log_path_override=self.pacman_log_path,
            gpg_dir_override=self.gpg_dir
        )
        self.builder = Builder(work_dir=self.work_dir)
        self.resolver = DependencyResolver(self.work_dir)
        self.generator = PyPIGenerator()

    def build_all(self, target_pkg, nocheck=False):
        logger.info(f"Resolving dependencies for {target_pkg}...")
        self.resolver.resolve(target_pkg)
        order = self.resolver.get_build_order()
        logger.info(f"Build order: {' -> '.join(order)}")

        for pkg in order:
            node_data = self.resolver.graph.nodes[pkg]
            tier = node_data.get("tier")

            # Check if already built in this run or previous
            current_state = self.state.get_package(pkg)
            if current_state and current_state.get("status") == "success":
                logger.info(f"Package {pkg} already built, skipping.")
                continue

            logger.info(f"Processing {pkg} (Tier: {tier})...")

            if tier == "repo":
                logger.info(f"{pkg} is in official repos, no build needed.")
                continue

            pkg_dir = None
            if tier == "local":
                pkg_dir = node_data["path"]
            elif tier == "aur":
                pkg_dir = clone_aur_repo(pkg, self.aur_cache_dir)
                if not pkg_dir:
                    logger.error(f"Failed to clone AUR repo for {pkg}")
                    self.state.update_package(pkg, "failed", "clone_error")
                    break
            elif tier == "pypi":
                pyname = node_data.get("pyname") or pkg.replace("python-", "")
                pkg_dir = os.path.join(self.generated_dir, pkg)
                depends = list(self.resolver.graph.successors(pkg))
                self.generator.generate(pyname, pkg_dir, depends=depends)
                generate_srcinfo(pkg_dir)

            if pkg_dir:
                try:
                    # Generate custom pacman.conf for host-side builds to find local deps
                    custom_conf = self.repo.generate_custom_conf(
                        output_path=self.pacman_conf_path
                    )

                    # Sync local repo to allow pacman to find freshly built dependencies
                    try:
                        # If we have a local repo db, we should sync it
                        sync_cmd = ["pacman", "-Sy", "--config", custom_conf, "--dbpath", self.pacman_db_path]
                        run_command(sync_cmd)
                    except subprocess.CalledProcessError as e:
                            logger.error(f"Error syncing pacman: {e.output}")
                            raise
                    pkg_file = self.builder.build(
                        pkg,
                        os.path.abspath(pkg_dir),
                        deps=self.repo.get_package_files(),
                        nocheck=nocheck,
                        custom_conf=custom_conf,
                    )
                    self.repo.add_package(pkg_file)
                    self.state.update_package(pkg, "built", "success")
                    logger.info(f"Successfully built and added {pkg}")
                except Exception as e:
                    logger.error(f"Failed to build {pkg}: {e}")
                    self.state.update_package(pkg, "failed", "error")
                    break
