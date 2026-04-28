import logging
import os
from jinja2 import Environment, PackageLoader, select_autoescape
from aur_python_packer.clients import PyPIClient
from aur_python_packer.metadata import MetadataParser

logger = logging.getLogger(__name__)

class PyPIGenerator:
    """
    Generates Arch Linux PKGBUILDs for Python packages using PyPI metadata
    and Jinja2 templates.
    """
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("aur_python_packer", "templates"),
            autoescape=select_autoescape()
        )
        self.template = self.env.get_template("PKGBUILD.j2")
        self.pypi_client = PyPIClient()
        self.metadata_parser = MetadataParser()

    def render(self, meta):
        """
        Renders the PKGBUILD template with the provided metadata.
        """
        return self.template.render(**meta)

    def normalize_license(self, meta):
        """
        Heuristic to normalize PyPI license strings/classifiers to SPDX identifiers
        or common Arch Linux license names.
        """
        # Priority 1: Check standard license classifiers
        for c in meta.get("classifiers", []):
            if c.startswith("License :: OSI Approved :: "):
                l = c.split(" :: ")[-1]
                logger.debug(f"Applying license heuristic (classifier): {l}")
                if "BSD License" in l: return "BSD-3-Clause"
                if "MIT License" in l: return "MIT"
                if "Apache Software License" in l: return "Apache-2.0"

        # Priority 2: Use the free-text license field
        l = meta.get("license", "None")
        # Heuristic: if it's very long or contains newlines, it's likely a license text,
        # not a name. Mark it as 'custom' unless we can find a keyword.
        if len(l) > 100 or "\n" in l:
             logger.debug("Applying license heuristic (long field -> custom)")
             if "BSD" in l: return "BSD-3-Clause"
             return "custom"
        return l

    def generate(self, pyname, output_dir, depends=None):
        """
        Orchestrates metadata retrieval and file generation for a Python package.
        """
        logger.info(f"Generating PKGBUILD for {pyname} in {output_dir}")
        meta = self.pypi_client.get_metadata(pyname)
        release_info = self.pypi_client.get_release_info(pyname, meta["version"])

        # Minimal default makedepends
        makedepends = ['python-build', 'python-installer', 'python-setuptools', 'python-wheel']
        if any("hatchling" in str(d).lower() for d in meta["requires_dist"]):
             makedepends.append('python-hatchling')

        norm_license = self.normalize_license(meta)

        pkg_data = {
            "pkgname": f"python-{pyname.lower()}",
            "pyname": pyname,
            "pkgver": meta["version"],
            # Heuristic: ensure summary is single-line to avoid breaking PKGBUILD
            "pkgdesc": meta["summary"],
            "url": meta["home_page"],
            "license": norm_license,
            "sha256": "SKIP", # Will be updated by updpkgsums
            "source_url": release_info["url"] if release_info else "",
            "depends": depends or [],
            "makedepends": makedepends,
        }

        os.makedirs(output_dir, exist_ok=True)
        pkgbuild_path = os.path.join(output_dir, "PKGBUILD")
        with open(pkgbuild_path, "w") as f:
            logger.debug(f"Generating PKGBUILD at {pkgbuild_path}")
            f.write(self.render(pkg_data))
        return pkgbuild_path

def generate_srcinfo(directory):
    """
    Static helper to regenerate .SRCINFO using the MetadataParser.
    Used mainly by the resolver.
    """
    parser = MetadataParser()
    parser.generate_srcinfo(directory)
