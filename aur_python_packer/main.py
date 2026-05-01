import logging
import os
import shlex
import subprocess

from aur_python_packer.builder import Builder
from aur_python_packer.generator import PyPIGenerator
from aur_python_packer.graph_utils import print_dependency_graph
from aur_python_packer.repo import RepoManager
from aur_python_packer.resolver import DependencyResolver
from aur_python_packer.state import StateManager
from aur_python_packer.utils import run_command
from aur_python_packer.clients import AURClient
from aur_python_packer.metadata import MetadataParser

logger = logging.getLogger(__name__)


class Manager:
    """
    The primary orchestrator for the AUR Python Packer.
    Coordinates dependency resolution, package generation, and sandboxed building.
    """

    def __init__(self, work_dir="work"):
        self.work_dir = os.path.abspath(work_dir)
        os.makedirs(self.work_dir, exist_ok=True)

        self.srv_dir = os.path.join(self.work_dir, "srv")
        self.state_file = os.path.join(self.srv_dir, "build_index.json")
        self.repo_dir = os.path.join(self.work_dir, "local_repo")
        self.aur_packages_dir = os.path.join(self.work_dir, "aur_packages")
        self.packages_dir = os.path.join(self.work_dir, "packages")
        self.pacman_conf_path = os.path.join(self.srv_dir, "pacman.conf")
        self.pacman_db_path = os.path.join(self.srv_dir, "pacman_db")
        self.pacman_cache_path = os.path.join(self.srv_dir, "pacman_cache")
        self.pacman_log_path = os.path.join(self.srv_dir, "pacman.log")
        self.gpg_dir = os.path.join(self.srv_dir, "gnupg")

        # Ensure core directories exist
        for d in [
            self.srv_dir,
            self.repo_dir,
            self.aur_packages_dir,
            self.packages_dir,
        ]:
            os.makedirs(d, exist_ok=True)

        self.state = StateManager(self.state_file)
        self.repo = RepoManager(
            self.repo_dir,
            db_path_override=self.pacman_db_path,
            cache_path_override=self.pacman_cache_path,
            log_path_override=self.pacman_log_path,
            gpg_dir_override=self.gpg_dir,
        )
        self.builder = Builder(work_dir=self.work_dir)
        self.resolver = DependencyResolver(
            self.work_dir, search_paths=[self.packages_dir, self.aur_packages_dir]
        )
        self.generator = PyPIGenerator()
        self.aur_client = AURClient()
        self.metadata_parser = MetadataParser()

    def build_all(self, target_pkg, nocheck=False, inject_depends=None):
        """
        Resolves and builds the specified target package and all its dependencies
        in the correct order.

        If inject_depends is provided, those deps are added to the target's graph
        as dependency edges, resolved through the standard 4-tier process.
        """
        logger.info(f"Resolving dependencies for {target_pkg}...")
        self.resolver.resolve(target_pkg)

        # Inject extra dependencies into the graph
        if inject_depends:
            for dep in inject_depends:
                self.resolver.inject_dependency(target_pkg, dep)

        order = self.resolver.get_build_order()
        logger.info(f"Build order: {' -> '.join(order)}")

        injected = list(inject_depends) if inject_depends else []

        # Show initial graph
        print_dependency_graph(self.resolver.graph, self.state)

        for pkg in order:
            node_data = self.resolver.graph.nodes[pkg]
            tier = node_data.get("tier")

            # Check if already built in this run or previous
            current_state = self.state.get_package(pkg)
            if (
                current_state
                and current_state.get("status") == "success"
                and current_state.get("version") == node_data.get("version")
            ):
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
                pkg_dir = node_data.get("path")
                if not pkg_dir:
                    logger.error(f"AUR package {pkg} has no source path")
                    self.state.update_package(
                        pkg, node_data.get("version", "unknown"), "failed"
                    )
                    break
            elif tier == "pypi":
                pyname = node_data.get("pyname") or pkg.replace("python-", "")
                pkg_dir = os.path.join(self.packages_dir, pkg)
                if not os.path.exists(os.path.join(pkg_dir, "PKGBUILD")):
                    depends = list(self.resolver.graph.successors(pkg))
                    self.generator.generate(pyname, pkg_dir, depends=depends)
                    # Use sandbox to run updpkgsums and makepkg --printsrcinfo
                    # updpkgsums needs network to download the source
                    self.run_in_sandbox("updpkgsums", cwd=pkg_dir, share_net=True)

                    # Generate .SRCINFO
                    self.metadata_parser.generate_srcinfo(pkg_dir)

            if pkg_dir:
                try:
                    # Generate custom pacman.conf for host-side builds to find local deps
                    custom_conf = self.repo.generate_custom_conf(
                        output_path=self.pacman_conf_path
                    )

                    self._sync_pacman(custom_conf)

                    version = node_data.get("version", "unknown")
                    try:
                        pkg_file = self.builder.build(
                            pkg,
                            os.path.abspath(pkg_dir),
                            deps=self.repo.get_package_files(),
                            nocheck=nocheck,
                            custom_conf=custom_conf,
                            pacman_db_path=self.pacman_db_path,
                        )
                        skipped = nocheck
                    except Exception as e:
                        if not nocheck:
                            logger.info(
                                f"Build failed for {pkg}, retrying with --nocheck..."
                            )
                            pkg_file = self.builder.build(
                                pkg,
                                os.path.abspath(pkg_dir),
                                deps=self.repo.get_package_files(),
                                nocheck=True,
                                custom_conf=custom_conf,
                                pacman_db_path=self.pacman_db_path,
                            )
                            skipped = True
                        else:
                            raise e

                    self.repo.add_package(pkg_file)
                    self.state.update_package(
                        pkg,
                        version,
                        "success",
                        skipped_checks=skipped,
                        injected_depends=injected if pkg == target_pkg else None,
                    )
                    logger.info(f"Successfully built and added {pkg}")

                    # Show updated graph
                    print_dependency_graph(self.resolver.graph, self.state)
                except Exception as e:
                    logger.error(f"Failed to build {pkg}: {e}")
                    self.state.update_package(pkg, version, "failed")
                    break

    def _sync_pacman(self, custom_conf):
        """Sync local repo to allow pacman to find packages."""
        logger.debug("Syncing pacman databases inside the sandbox-friendly environment")
        sync_cmd = [
            "pacman",
            "-Sy",
            "--config",
            custom_conf,
            "--dbpath",
            self.pacman_db_path,
        ]
        self.builder.sandbox.run_host_command(sync_cmd)

    def git_init_all(self):
        """Initialize Git repos in all package directories using sandboxed git."""
        logger.info("Initializing Git repositories in package directories...")
        for base_dir in [self.packages_dir, self.aur_packages_dir]:
            if not os.path.isdir(base_dir):
                continue
            for pkg_name in sorted(os.listdir(base_dir)):
                pkg_dir = os.path.join(base_dir, pkg_name)
                if not os.path.isdir(pkg_dir):
                    continue
                git_dir = os.path.join(pkg_dir, ".git")
                if os.path.exists(git_dir):
                    logger.debug(f"Git repo already exists in {pkg_dir}")
                    continue
                self._git_init_in_dir(pkg_dir)

    def _git_init_in_dir(self, pkg_dir):
        """Initialize a git repo in the directory and create initial commit."""
        pkg_name = os.path.basename(pkg_dir)
        logger.info(f"Initializing git repo in {pkg_dir}")

        # Configure git user
        self.run_in_sandbox(
            [
                "git",
                "config",
                "--global",
                "user.email",
                "aur-packer@localhost",
            ],
            cwd=pkg_dir,
            check=False,
            log_level=logging.DEBUG,
        )
        self.run_in_sandbox(
            ["git", "config", "--global", "user.name", "AUR Packer"],
            cwd=pkg_dir,
            check=False,
            log_level=logging.DEBUG,
        )

        # Init and initial commit
        self.run_in_sandbox(["git", "init"], cwd=pkg_dir, log_level=logging.DEBUG)
        self.run_in_sandbox(
            ["git", "add", "-A"], cwd=pkg_dir, log_level=logging.DEBUG
        )
        self.run_in_sandbox(
            ["git", "commit", "-m", f"Initial package generation/clone ({pkg_name})"],
            cwd=pkg_dir,
            check=False,
            log_level=logging.DEBUG,
        )

    def git_show_changed(self):
        """Return list of package names with uncommitted PKGBUILD changes."""
        logger.info("Checking for uncommitted changes...")
        changed = []
        for base_dir in [self.packages_dir, self.aur_packages_dir]:
            if not os.path.isdir(base_dir):
                continue
            for pkg_name in sorted(os.listdir(base_dir)):
                pkg_dir = os.path.join(base_dir, pkg_name)
                if not os.path.isdir(pkg_dir):
                    continue
                git_dir = os.path.join(pkg_dir, ".git")
                if not os.path.exists(git_dir):
                    logger.debug(f"No git repo in {pkg_dir}, skipping.")
                    continue
                result = run_command(
                    ["git", "diff", "--name-only", "HEAD", "--", "PKGBUILD"],
                    cwd=pkg_dir,
                    check=False,
                    log_level=logging.DEBUG,
                )
                if result.returncode == 0 and result.stdout.strip():
                    changed.append(pkg_name)
        return changed

    def run_in_sandbox(
        self, command, cwd=None, log_level=logging.INFO, check=True, share_net=False
    ):
        """
        Executes an arbitrary command inside the sandboxed build environment.
        """
        if cwd is None:
            cwd = self.work_dir

        custom_conf = self.repo.generate_custom_conf(output_path=self.pacman_conf_path)
        self.builder._bootstrap_root(custom_conf, self.pacman_db_path)

        self._sync_pacman(custom_conf)

        if isinstance(command, str):
            cmd_list = shlex.split(command)
        else:
            cmd_list = command

        logger.info(f"Executing in sandbox: {' '.join(cmd_list)}")
        return self.builder._run_in_sandbox(
            cmd_list,
            cwd=os.path.abspath(cwd),
            custom_conf=custom_conf,
            pacman_db_path=self.pacman_db_path,
            log_level=log_level,
            check=check,
            share_net=share_net,
        )
