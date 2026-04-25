import os
import re


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


import networkx as nx


class DependencyResolver:
    def __init__(self, search_paths=None):
        self.graph = nx.DiGraph()
        self.search_paths = search_paths or [".", ".."]
        self.visited = set()

    def get_build_order(self):
        try:
            return list(reversed(list(nx.topological_sort(self.graph))))
        except nx.NetworkXUnfeasible:
            raise ValueError("Circular dependency detected")

    def resolve(self, pkgname):
        if pkgname in self.visited:
            return
        self.visited.add(pkgname)

        # 1. Check Local
        local_meta = self._find_local(pkgname)
        if local_meta:
            self.graph.add_node(pkgname, tier="local", path=local_meta["path"])
            for dep in local_meta.get("depends", []):
                self.graph.add_edge(pkgname, dep)
                self.resolve(dep)
            return

        # 2. Check Repos
        if is_in_repos(pkgname):
            self.graph.add_node(pkgname, tier="repo")
            return

        # 3. Check AUR
        aur_meta = get_aur_info(pkgname)
        if aur_meta:
            self.graph.add_node(pkgname, tier="aur")
            # AUR RPC returns Depends and MakeDepends
            deps = aur_meta.get("Depends", []) + aur_meta.get("MakeDepends", [])
            for dep in deps:
                # Strip version constraints
                dep_name = re.split("[<>=]", dep)[0]
                self.graph.add_edge(pkgname, dep_name)
                self.resolve(dep_name)
            return

        # 4. Check PyPI (Simplified for now, will expand in Phase 3)
        if pkgname.startswith("python-"):
            self.graph.add_node(pkgname, tier="pypi")
            return

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


import subprocess


def is_in_repos(pkgname):
    """Check if package is in official repos."""
    try:
        subprocess.run(["pacman", "-Si", pkgname], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


import requests


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
