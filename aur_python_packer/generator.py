import hashlib
import logging
import os
import subprocess

import requests
from jinja2 import Template

from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)

PKGBUILD_TEMPLATE = """
pkgname={{ pkgname }}
_name={{ pyname }}
pkgver={{ pkgver }}
pkgrel=1
pkgdesc="{{ pkgdesc }}"
arch=('any')
url="{{ url }}"
license=('{{ license }}')
depends=({% for dep in depends %}'{{ dep }}' {% endfor %})
makedepends=('python-build' 'python-installer' 'python-setuptools' 'python-wheel')
source=("{{ source_url }}")
sha256sums=('{{ sha256 }}')

build() {
    cd "$srcdir/$_name-$pkgver"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/$_name-$pkgver"
    python -m installer --destdir="$pkgdir" dist/*.whl
}
"""


class PyPIGenerator:
    def __init__(self):
        self.template = Template(PKGBUILD_TEMPLATE)

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
                    "sha256": release["digests"]["sha256"],
                    "url": release["url"]
                }
        return None

    def render(self, meta):
        return self.template.render(**meta)

    def generate(self, pyname, output_dir, depends=None):
        meta = self.fetch_meta(pyname)
        release_info = self.get_release_info(pyname, meta["version"])

        # Clean up license: take first line, remove common suffixes
        license = meta["license"].split('\n')[0]
        for suffix in [" License", " (BSD)"]:
            if license.endswith(suffix):
                license = license[:-len(suffix)]

        pkg_data = {
            "pkgname": f"python-{pyname.lower()}",
            "pyname": pyname,
            "pkgver": meta["version"],
            "pkgdesc": meta["summary"],
            "url": meta["home_page"],
            "license": license,
            "sha256": release_info["sha256"] if release_info else "",
            "source_url": release_info["url"] if release_info else "",
            "depends": depends or [],
        }

        os.makedirs(output_dir, exist_ok=True)
        pkgbuild_path = os.path.join(output_dir, "PKGBUILD")
        with open(pkgbuild_path, "w") as f:
            logger.debug(f"Generating PKGBUILD at {pkgbuild_path}")
            f.write(self.render(pkg_data))
        return pkgbuild_path


def generate_srcinfo(directory):
    """Run makepkg --printsrcinfo and save to .SRCINFO."""
    try:
        logger.debug(f"Generating .SRCINFO in {directory}")
        result = run_command(["makepkg", "--printsrcinfo"], cwd=directory)
        with open(os.path.join(directory, ".SRCINFO"), "w") as f:
            f.write(result.stdout)
        return True
    except subprocess.CalledProcessError:
        logger.error(f"Failed to generate .SRCINFO in {directory}")
        return False
