import logging
import os
import requests
from jinja2 import Environment, PackageLoader, select_autoescape

from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)

class PyPIGenerator:
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("aur_python_packer", "templates"),
            autoescape=select_autoescape()
        )
        self.template = self.env.get_template("PKGBUILD.j2")

    def fetch_meta(self, pyname):
        logger.debug(f"Fetching PyPI metadata for {pyname}")
        url = f"https://pypi.org/pypi/{pyname}/json"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        info = data["info"]
        return {
            "name": info["name"],
            "version": info["version"],
            "summary": info["summary"],
            "home_page": info.get("home_page") or info.get("project_url"),
            "license": info.get("license") or "None",
            "classifiers": info.get("classifiers") or [],
            "requires_dist": info.get("requires_dist") or [],
        }

    def get_release_info(self, pyname, version):
        # This is a bit complex as we need to find the correct sdist URL
        logger.debug(f"Fetching PyPI release info for {pyname}=={version}")
        url = f"https://pypi.org/pypi/{pyname}/{version}/json"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        for release in data["urls"]:
            if release["packagetype"] == "sdist":
                return {
                    "url": release["url"]
                }
        return None

    def render(self, meta):
        return self.template.render(**meta)

    def normalize_license(self, meta):
        # Try to find license in classifiers first
        for c in meta["classifiers"]:
            if c.startswith("License :: OSI Approved :: "):
                l = c.split(" :: ")[-1]
                if "BSD License" in l: return "BSD-3-Clause"
                if "MIT License" in l: return "MIT"
                if "Apache Software License" in l: return "Apache-2.0"

        # Fallback to license field with some heuristics
        l = meta["license"]
        if len(l) > 100 or "\n" in l:
             if "BSD" in l: return "BSD-3-Clause"
             return "custom"
        return l

    def generate(self, pyname, output_dir, depends=None):
        meta = self.fetch_meta(pyname)
        release_info = self.get_release_info(pyname, meta["version"])

        # Minimal default makedepends
        makedepends = ['python-build', 'python-installer', 'python-setuptools', 'python-wheel']
        if any("hatchling" in str(d).lower() for d in meta["requires_dist"]):
             makedepends.append('python-hatchling')

        norm_license = self.normalize_license(meta)

        pkg_data = {
            "pkgname": f"python-{pyname.lower()}",
            "pyname": pyname,
            "pkgver": meta["version"],
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
    """Regenerate .SRCINFO using makepkg."""
    cmd = ["makepkg", "--printsrcinfo"]
    result = run_command(cmd, cwd=directory)
    with open(os.path.join(directory, ".SRCINFO"), "w") as f:
        f.write(result.stdout)
