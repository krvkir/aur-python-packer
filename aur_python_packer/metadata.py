import os
import re
import logging
from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)

class MetadataParser:
    """
    Handles parsing and generation of Arch Linux package metadata files
    (.SRCINFO and PKGBUILD).
    """

    def parse_srcinfo(self, path):
        """
        Parse .SRCINFO and return pkgname and depends.
        
        This is the preferred way to get metadata as it's the source of truth
        for AUR packages after makepkg has processed the PKGBUILD.
        """
        deps = []
        pkgname = None
        if not os.path.exists(path):
            logger.debug(f"Metadata file not found: {path}")
            return None

        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                # We're interested in pkgname and dependency fields
                # Note: .SRCINFO can have multiple pkgname if it's a split package,
                # but for Python packages we usually have one.
                if line.startswith("pkgname = "):
                    pkgname = line.split(" = ")[1]
                elif line.startswith("depends = ") or line.startswith("makedepends = "):
                    dep = line.split(" = ")[1]
                    # Strip version constraints like 'python-foo>=1.0'
                    dep = re.split("[<>=]", dep)[0]
                    deps.append(dep)
        return {"pkgname": pkgname, "depends": list(set(deps))}

    def parse_pkgbuild(self, path):
        """
        Simple regex parser for PKGBUILD if .SRCINFO is missing.
        
        WARNING: This is less reliable than .SRCINFO parsing as it doesn't 
        handle shell variable expansion or complex bash arrays perfectly.
        """
        metadata = {}
        if not os.path.exists(path):
            logger.debug(f"PKGBUILD not found: {path}")
            return None

        with open(path, "r") as f:
            content = f.read()
            # Basic regex to find pkgname assignment
            pkgname_match = re.search(r"pkgname=(?P<name>[^\n]+)", content)
            if pkgname_match:
                metadata["pkgname"] = pkgname_match.group("name").strip("\"'")

            all_deps = []
            # Extract dependencies from depends and makedepends arrays
            for key in ["depends", "makedepends"]:
                match = re.search(
                    rf"{key}=\((?P<deps>[^\)]+)\)", content, re.MULTILINE
                )
                if match:
                    deps_str = match.group("deps")
                    deps = [d.strip("\"'") for d in deps_str.split()]
                    all_deps.extend([re.split("[<>=]", d)[0] for d in deps])
            metadata["depends"] = list(set(all_deps))
        return metadata

    def generate_srcinfo(self, directory):
        """
        Regenerate .SRCINFO using makepkg.
        
        Calls `makepkg --printsrcinfo` and saves the result to .SRCINFO in the given directory.
        """
        logger.debug(f"Generating .SRCINFO in {directory}")
        cmd = ["makepkg", "--printsrcinfo"]
        result = run_command(cmd, cwd=directory)
        with open(os.path.join(directory, ".SRCINFO"), "w") as f:
            f.write(result.stdout)
