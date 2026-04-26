import hashlib
import os
import subprocess

import requests
from jinja2 import Template

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
source=("https://files.pythonhosted.org/packages/source/${_name::1}/$_name/$_name-$pkgver.tar.gz")
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

    def get_sha256(self, pyname, version):
        # This is a bit complex as we need to find the correct sdist URL
        url = f"https://pypi.org/pypi/{pyname}/{version}/json"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        for release in data["urls"]:
            if release["packagetype"] == "sdist":
                return release["digests"]["sha256"]
        return None

    def render(self, meta):
        return self.template.render(**meta)

    def generate(self, pyname, output_dir, depends=None):
        meta = self.fetch_meta(pyname)
        sha256 = self.get_sha256(pyname, meta["version"])

        pkg_data = {
            "pkgname": f"python-{pyname.lower()}",
            "pyname": pyname,
            "pkgver": meta["version"],
            "pkgdesc": meta["summary"],
            "url": meta["home_page"],
            "license": meta["license"],
            "sha256": sha256,
            "depends": depends or [],
        }

        os.makedirs(output_dir, exist_ok=True)
        pkgbuild_path = os.path.join(output_dir, "PKGBUILD")
        with open(pkgbuild_path, "w") as f:
            f.write(self.render(pkg_data))
        return pkgbuild_path


def generate_srcinfo(directory):
    """Run makepkg --printsrcinfo and save to .SRCINFO."""
    try:
        result = subprocess.run(
            ["makepkg", "--printsrcinfo"],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True,
        )
        with open(os.path.join(directory, ".SRCINFO"), "w") as f:
            f.write(result.stdout)
        return True
    except subprocess.CalledProcessError:
        return False
