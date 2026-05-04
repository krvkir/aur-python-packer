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

    def __init__(self, maintainer="AUR Packer <aur-packer@localhost>", cache=None):
        self.env = Environment(
            loader=PackageLoader("aur_python_packer", "templates"),
            autoescape=select_autoescape(),
        )
        self.template = self.env.get_template("PKGBUILD.j2")
        self.pypi_client = PyPIClient(cache=cache)
        self.metadata_parser = MetadataParser()
        self.maintainer = maintainer

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
        # Mapping for common license strings
        mapping = {
            "Apache Software License": "Apache-2.0",
            "MIT License": "MIT",
            "BSD License": "BSD-3-Clause",
        }

        # Priority 1: Check standard license classifiers
        for c in meta.get("classifiers", []):
            if c.startswith("License :: OSI Approved :: "):
                l = c.split(" :: ")[-1]
                logger.debug(f"Applying license heuristic (classifier): {l}")
                for key, value in mapping.items():
                    if key in l:
                        return value

        # Priority 2: Use the free-text license field
        l = meta.get("license", "None")

        # Check mapping in free-text field
        for key, value in mapping.items():
            if key in l:
                return value

        # Heuristic: if it's very long or contains newlines, it's likely a license text,
        # not a name. Mark it as 'custom' unless we can find a keyword.
        if len(l) > 100 or "\n" in l:
            logger.debug("Applying license heuristic (long field -> custom)")
            if "BSD" in l:
                return "BSD-3-Clause"
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
        makedepends = [
            "python-build",
            "python-installer",
            "python-setuptools",
            "python-wheel",
        ]
        if any("hatchling" in str(d).lower() for d in meta["requires_dist"]):
            makedepends.append("python-hatchling")

        norm_license = self.normalize_license(meta)

        source_url = release_info["url"] if release_info else ""
        src_folder = f"{pyname}-{meta['version']}"

        if release_info and "filename" in release_info:
            filename = release_info["filename"]
            version = meta["version"]

            # Identify extension
            ext = ""
            for e in [".tar.gz", ".tar.bz2", ".tar.xz", ".zip"]:
                if filename.endswith(e):
                    ext = e
                    break

            base_filename = filename[: -len(ext)] if ext else filename

            # Detect pattern to use bash variables in PKGBUILD
            if base_filename == f"{pyname}-{version}":
                source_filename = f"$_name-$pkgver{ext}"
                src_folder = f"$_name-$pkgver"
            elif base_filename == f"{pyname.replace('-', '_')}-{version}":
                source_filename = f"${{_name//-/_}}-$pkgver{ext}"
                src_folder = f"${{_name//-/_}}-$pkgver"
            else:
                # Fallback to hardcoded filename if it doesn't follow standard patterns
                source_filename = filename
                src_folder = base_filename

            source_url = f"https://files.pythonhosted.org/packages/source/${{_name::1}}/$_name/{source_filename}"

        pkg_data = {
            "maintainer": self.maintainer,
            "pkgname": f"python-{pyname.lower()}",
            "pyname": pyname,
            "pkgver": meta["version"],
            "pkgdesc": meta["summary"],
            "url": meta.get("home_page") or f"https://pypi.org/project/{pyname}/",
            "license": norm_license,
            "sha256": "SKIP",  # Will be updated by updpkgsums
            "source_url": source_url,
            "src_folder": src_folder,
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
