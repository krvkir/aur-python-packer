import logging
import json
import os
import re
import networkx as nx
from packaging.requirements import Requirement
from aur_python_packer.utils import run_command
from aur_python_packer.metadata import MetadataParser
from aur_python_packer.clients import PyPIClient, AURClient

logger = logging.getLogger(__name__)


class DependencyResolver:
    """
    Resolves a recursive dependency tree for a given package across
    Local, Repo, AUR, and PyPI tiers.
    """

    def __init__(self, work_dir=None, search_paths=None):
        self.graph = nx.DiGraph()
        self.work_dir = work_dir
        self.search_paths = search_paths or ["."]
        if work_dir and work_dir not in self.search_paths:
            self.search_paths.append(work_dir)

        self.packages_dir = (
            os.path.join(work_dir, "packages") if work_dir else None
        )
        self.aur_packages_dir = (
            os.path.join(work_dir, "aur_packages") if work_dir else None
        )

        self.visited = set()
        self.mapping = self._load_mapping()
        self.metadata_parser = MetadataParser()
        self.pypi_client = PyPIClient()
        self.aur_client = AURClient()

    def get_build_order(self):
        """
        Calculates a valid build order using topological sort (leaves first).
        """
        try:
            return list(reversed(list(nx.topological_sort(self.graph))))
        except nx.NetworkXUnfeasible:
            logger.error("Circular dependency detected in the dependency graph.")
            raise ValueError("Circular dependency detected")

    def _load_mapping(self):
        """
        Loads explicit PyPI-to-Arch name mappings from a JSON file.
        """
        if self.work_dir:
            mapping_path = os.path.join(self.work_dir, "pypi_mapping.json")
            if os.path.exists(mapping_path):
                with open(mapping_path, "r") as f:
                    return json.load(f)
        return {}

    def normalize_pypi_name(self, name):
        """
        Normalizes a PyPI package name to a likely Arch Linux package name.

        Follows standard 'python-pkgname' naming convention and checks official repos.
        """
        name_lower = name.lower().replace("_", "-")

        # 1. Check explicit mapping
        if name_lower in self.mapping:
            return self.mapping[name_lower]

        # 2. Check if name or python-name exists in repos (trivial cases)
        for candidate in [name_lower, f"python-{name_lower}"]:
            provider = find_provider_in_repos(candidate)
            if provider:
                return provider

        # 3. Default
        return f"python-{name_lower}"

    def parse_pypi_dependency(self, req_str):
        """
        Parses a PEP 508 dependency string and returns the corresponding Arch package name.
        """
        req = Requirement(req_str)
        # Heuristic: Skip extra/optional dependencies (e.g. [test], [doc]) for now
        if req.marker and "extra ==" in str(req.marker):
            logger.debug(f"Skipping optional PyPI dependency: {req_str}")
            return None
        return self.normalize_pypi_name(req.name)

    def pypi_get_dependencies(self, pyname):
        """
        Retrieves a list of Arch Linux dependency names for a PyPI package.
        """
        try:
            meta = self.pypi_client.get_metadata(pyname)
            deps = []
            requires_dist = meta.get("requires_dist", [])
            for req_str in requires_dist:
                arch_dep = self.parse_pypi_dependency(req_str)
                if arch_dep:
                    deps.append(arch_dep)
            return deps
        except Exception:
            return []

    def inject_dependency(self, target_pkg, dep_name):
        """
        Injects an ad-hoc dependency into the resolution graph.

        The dependency is resolved through the standard 4-tier process first,
        then an edge from target_pkg -> dep_name is added.
        """
        logger.info(f"Injecting dependency: {dep_name} -> {target_pkg}")
        self.resolve(dep_name)
        self.graph.add_edge(target_pkg, dep_name)

    def resolve(self, pkgname):
        """
        Recursively resolves dependencies for a package following a 4-tier sequence.
        """
        if pkgname in self.visited:
            return
        self.visited.add(pkgname)

        logger.debug(f"Resolving dependency: {pkgname}")

        # Tier 1: Newly Created Packages
        if self.packages_dir:
            meta = self._find_in_dir(pkgname, self.packages_dir)
            if meta:
                logger.debug(f"Found {pkgname} in newly created packages")
                self._add_to_graph(pkgname, meta, tier="local")
                return

        # Tier 2: Official Repositories
        provider = find_provider_in_repos(pkgname)
        if provider:
            logger.debug(
                f"Found {pkgname} in official repositories (provider: {provider})"
            )
            if provider != pkgname:
                self.graph.add_node(provider, tier="repo")
                self.graph.add_edge(pkgname, provider)
            else:
                self.graph.add_node(pkgname, tier="repo")
            return

        # Tier 3: AUR (Local Clones)
        if self.aur_packages_dir:
            meta = self._find_in_dir(pkgname, self.aur_packages_dir)
            if meta:
                logger.debug(f"Found {pkgname} in local AUR clones")
                self._add_to_graph(pkgname, meta, tier="aur")
                return

        # Tier 4: AUR (Remote RPC + Clone)
        aur_meta = self.aur_client.get_info(pkgname)
        if aur_meta:
            logger.info(f"Found {pkgname} in AUR, cloning immediately...")
            if self.aur_packages_dir:
                pkg_dir = self.aur_client.clone_repo(pkgname, self.aur_packages_dir)
                if pkg_dir:
                    meta = self._find_in_dir(pkgname, self.aur_packages_dir)
                    if meta:
                        self._add_to_graph(pkgname, meta, tier="aur")
                        return

            # Fallback if clone failed or no dir set
            deps = (
                aur_meta.get("Depends", [])
                + aur_meta.get("MakeDepends", [])
                + aur_meta.get("CheckDepends", [])
            )
            self.graph.add_node(
                pkgname,
                tier="aur",
                version=aur_meta.get("Version"),
            )
            for dep in deps:
                dep_name = re.split("[<>=]", dep)[0]
                self.graph.add_edge(pkgname, dep_name)
                self.resolve(dep_name)
            return

        # Tier 5: PyPI
        pyname = pkgname
        if pkgname.startswith("python-"):
            pyname = pkgname[7:]

        if self.pypi_client.verify_existence(pyname):
            logger.debug(f"Found {pyname} on PyPI")
            arch_name = self.normalize_pypi_name(pyname)
            if pkgname != arch_name:
                self.resolve(arch_name)
                self.graph.add_edge(pkgname, arch_name)
                return

            pypi_meta = self.pypi_client.get_metadata(pyname)
            self.graph.add_node(
                pkgname,
                tier="pypi",
                pyname=pyname,
                version=pypi_meta.get("version"),
            )
            deps = self.pypi_get_dependencies(pyname)
            for dep in deps:
                self.graph.add_edge(pkgname, dep)
                self.resolve(dep)
            return

        logger.error(f"Could not resolve dependency: {pkgname}")
        raise ValueError(f"Could not resolve dependency: {pkgname}")

    def _find_in_dir(self, pkgname, directory):
        """
        Searches for a subdirectory containing a PKGBUILD for the given package.
        """
        pkg_path = os.path.join(directory, pkgname)
        if os.path.isdir(pkg_path):
            pkgbuild_path = os.path.join(pkg_path, "PKGBUILD")
            if os.path.exists(pkgbuild_path):
                srcinfo_path = os.path.join(pkg_path, ".SRCINFO")
                # Check if .SRCINFO needs regeneration
                if not os.path.exists(srcinfo_path) or os.path.getmtime(
                    pkgbuild_path
                ) > os.path.getmtime(srcinfo_path):
                    logger.debug(
                        f".SRCINFO is missing or stale for {pkgname}, (re)generating..."
                    )
                    self.metadata_parser.generate_srcinfo(pkg_path)

                if os.path.exists(srcinfo_path):
                    meta = self.metadata_parser.parse_srcinfo(srcinfo_path)
                    if meta:
                        meta["path"] = pkg_path
                        return meta

                meta = self.metadata_parser.parse_pkgbuild(pkgbuild_path)
                if meta:
                    meta["path"] = pkg_path
                    return meta
        return None

    def _add_to_graph(self, pkgname, meta, tier):
        """Helper to add node and resolve its dependencies."""
        self.graph.add_node(
            pkgname,
            tier=tier,
            path=meta.get("path"),
            version=meta.get("pkgver") or meta.get("version"),
        )
        for dep in meta.get("depends", []):
            self.graph.add_edge(pkgname, dep)
            self.resolve(dep)


def find_provider_in_repos(pkgname):
    """
    Checks if a package or something providing it exists in official repos.
    Returns the actual package name if found, else None.
    """
    # 1. Direct hit
    result = run_command(["pacman", "-Ssq", f"^{pkgname}$"], check=False)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().splitlines()[0]

    # 2. Check provides
    result = run_command(
        ["pacman", "-Ssq", "--provides", f"^{pkgname}$"], check=False
    )
    if result.returncode == 0 and result.stdout.strip():
        providers = result.stdout.strip().splitlines()
        if providers:
            return providers[0]

    return None


def is_in_repos(pkgname):
    """
    Checks if a package exists in the official Arch Linux repositories.
    """
    return find_provider_in_repos(pkgname) is not None
