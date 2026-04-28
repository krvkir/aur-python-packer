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
        if work_dir and work_dir not in self.search_paths: self.search_paths.append(work_dir)
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
        name_lower = name.lower().replace('_', '-')
        
        # 1. Check explicit mapping
        if name_lower in self.mapping:
            return self.mapping[name_lower]
        
        # 2. Check if name or python-name exists in repos (trivial cases)
        for candidate in [name_lower, f"python-{name_lower}"]:
            if is_in_repos(candidate):
                return candidate
                
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

    def resolve(self, pkgname):
        """
        Recursively resolves dependencies for a package.
        
        Resolution Priority:
        1. Local directory (PKGBUILD/SRCINFO)
        2. Official Repositories
        3. AUR
        4. PyPI (Generates new package)
        """
        if pkgname in self.visited:
            return
        self.visited.add(pkgname)

        logger.debug(f"Resolving dependency: {pkgname}")

        # 1. Check Local
        local_meta = self._find_local(pkgname)
        if local_meta:
            logger.debug(f"Found {pkgname} locally at {local_meta['path']}")
            self.graph.add_node(pkgname, tier="local", path=local_meta["path"])
            for dep in local_meta.get("depends", []):
                self.graph.add_edge(pkgname, dep)
                self.resolve(dep)
            return

        # 2. Check Repos
        if is_in_repos(pkgname):
            logger.debug(f"Found {pkgname} in official repositories")
            self.graph.add_node(pkgname, tier="repo")
            return

        # 3. Check AUR
        aur_meta = self.aur_client.get_info(pkgname)
        if aur_meta:
            logger.debug(f"Found {pkgname} in AUR")
            self.graph.add_node(
                pkgname,
                tier="aur",
                version=aur_meta.get("Version"),
                pkgname=aur_meta.get("Name"),
            )
            # AUR RPC returns Depends, MakeDepends, and CheckDepends
            deps = (
                aur_meta.get("Depends", [])
                + aur_meta.get("MakeDepends", [])
                + aur_meta.get("CheckDepends", [])
            )
            for dep in deps:
                # Strip version constraints
                dep_name = re.split("[<>=]", dep)[0]
                self.graph.add_edge(pkgname, dep_name)
                self.resolve(dep_name)
            return

        # 4. Check PyPI
        pyname = pkgname
        if pkgname.startswith("python-"):
            pyname = pkgname[7:]

        if self.pypi_client.verify_existence(pyname):
            logger.debug(f"Found {pyname} on PyPI")
            arch_name = self.normalize_pypi_name(pyname)
            if pkgname != arch_name:
                # If we're resolving e.g. 'fastmcp', but it should be 'python-fastmcp',
                # redirect the resolution.
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

    def _find_local(self, pkgname):
        """
        Searches for a local directory containing a PKGBUILD for the given package.
        """
        for base in self.search_paths:
            pkg_path = os.path.join(base, pkgname)
            if os.path.isdir(pkg_path):
                pkgbuild_path = os.path.join(pkg_path, "PKGBUILD")
                if os.path.exists(pkgbuild_path):
                    srcinfo_path = os.path.join(pkg_path, ".SRCINFO")
                    # Check if .SRCINFO needs regeneration
                    if not os.path.exists(srcinfo_path) or os.path.getmtime(
                        pkgbuild_path
                    ) > os.path.getmtime(srcinfo_path):
                        logger.debug(f".SRCINFO is missing or stale for {pkgname}, (re)generating...")
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

def is_in_repos(pkgname):
    """
    Checks if a package exists in the official Arch Linux repositories.
    """
    result = run_command(["pacman", "-Si", pkgname], check=False)
    return result.returncode == 0
