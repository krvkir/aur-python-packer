import os
import logging
import re
import subprocess

import networkx as nx
import requests
from packaging.requirements import Requirement

from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)

def parse_srcinfo(path):
    """Parse .SRCINFO and return pkgname and depends."""
    depends = []
    pkgname = None
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("pkgname = "):
                pkgname = line.split(" = ")[1]
            elif line.startswith("depends = "):
                dep = line.split(" = ")[1]
                # Strip version constraints like 'python-foo>=1.0'
                dep = re.split("[<>=]", dep)[0]
                depends.append(dep)
    return {"pkgname": pkgname, "depends": depends}


def parse_pkgbuild(path):
    """Simple regex parser for PKGBUILD if .SRCINFO is missing."""
    # Note: This is less reliable than .SRCINFO
    metadata = {}
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        content = f.read()
        pkgname_match = re.search(r"pkgname=(?P<name>[^\n]+)", content)
        if pkgname_match:
            metadata["pkgname"] = pkgname_match.group("name").strip("\"'")

        # This is a very naive depends parser, won't handle arrays properly
        # but good enough for simple cases
        depends_match = re.search(
            r"depends=\((?P<deps>[^\)]+)\)", content, re.MULTILINE
        )
        if depends_match:
            deps_str = depends_match.group("deps")
            deps = [d.strip("\"'") for d in deps_str.split()]
            metadata["depends"] = [re.split("[<>=]", d)[0] for d in deps]
    return metadata


class DependencyResolver:
    def __init__(self, search_paths=None):
        self.graph = nx.DiGraph()
        self.search_paths = search_paths or ["."]
        self.visited = set()

    def get_build_order(self):
        try:
            return list(reversed(list(nx.topological_sort(self.graph))))
        except nx.NetworkXUnfeasible:
            logger.error("Circular dependency detected in the dependency graph.")
            raise ValueError("Circular dependency detected")

    def resolve(self, pkgname):
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
        aur_meta = get_aur_info(pkgname)
        if aur_meta:
            logger.debug(f"Found {pkgname} in AUR")
            self.graph.add_node(pkgname, tier="aur")
            # AUR RPC returns Depends and MakeDepends
            deps = aur_meta.get("Depends", []) + aur_meta.get("MakeDepends", [])
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

        if pypi_verify_existence(pyname):
            logger.debug(f"Found {pyname} on PyPI")
            arch_name = normalize_pypi_name(pyname)
            if pkgname != arch_name:
                self.resolve(arch_name)
                self.graph.add_edge(pkgname, arch_name)
                return

            self.graph.add_node(pkgname, tier="pypi", pyname=pyname)
            deps = pypi_get_dependencies(pyname)
            for dep in deps:
                self.graph.add_edge(pkgname, dep)
                self.resolve(dep)
            return

        logger.error(f"Could not resolve dependency: {pkgname}")
        raise ValueError(f"Could not resolve dependency: {pkgname}")

    def _find_local(self, pkgname):
        for base in self.search_paths:
            pkg_path = os.path.join(base, pkgname)
            if os.path.isdir(pkg_path):
                srcinfo_path = os.path.join(pkg_path, ".SRCINFO")
                if os.path.exists(srcinfo_path):
                    meta = parse_srcinfo(srcinfo_path)
                    meta["path"] = pkg_path
                    return meta
                pkgbuild_path = os.path.join(pkg_path, "PKGBUILD")
                if os.path.exists(pkgbuild_path):
                    meta = parse_pkgbuild(pkgbuild_path)
                    meta["path"] = pkg_path
                    return meta
        return None


def is_in_repos(pkgname):
    """Check if package is in official repos."""
    try:
        run_command(["pacman", "-Si", pkgname])
        return True
    except subprocess.CalledProcessError:
        return False


def normalize_pypi_name(name):
    """Normalize PyPI name to Arch python- package name."""
    return f"python-{name.lower().replace('_', '-')}"


def parse_pypi_dependency(req_str):
    """Parse PEP 508 dependency string and return Arch package name if it applies."""
    req = Requirement(req_str)
    # Skip extra dependencies (e.g. [test], [doc]) for now
    if req.marker:
        # This is a very basic marker check. If it contains 'extra ==', skip it.
        if 'extra ==' in str(req.marker):
            return None
    return normalize_pypi_name(req.name)


def pypi_get_dependencies(pyname):
    """Fetch dependencies for a PyPI package."""
    url = f"https://pypi.org/pypi/{pyname}/json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        requires_dist = data["info"].get("requires_dist") or []
        deps = []
        for req_str in requires_dist:
            arch_dep = parse_pypi_dependency(req_str)
            if arch_dep:
                deps.append(arch_dep)
        return deps
    except Exception:
        return []


def pypi_verify_existence(pyname):
    """Verify if a package exists on PyPI."""
    url = f"https://pypi.org/pypi/{pyname}/json"
    try:
        resp = requests.get(url, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False

def get_aur_info(pkgname):
    """Fetch package info from AUR RPC."""
    url = f"https://aur.archlinux.org/rpc/v5/info?arg[]={pkgname}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["resultcount"] > 0:
            return data["results"][0]
    except Exception:
        pass
    return None


def clone_aur_repo(pkgname, dest_parent):
    """Clone an AUR repository."""
    url = f"https://aur.archlinux.org/{pkgname}.git"
    dest_path = os.path.join(dest_parent, pkgname)
    if os.path.exists(dest_path):
        # Already exists, maybe update? For now just return path
        return dest_path

    try:
        run_command(["git", "clone", url, dest_path])
        return dest_path
    except subprocess.CalledProcessError:
        logger.error(f"Failed to clone AUR repo for {pkgname}")
        return None
