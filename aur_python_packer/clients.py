import logging
import requests
import os
from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)

class PyPIClient:
    """
    Client for interacting with the PyPI JSON API.
    """
    def __init__(self, timeout=10):
        self.timeout = timeout

    def get_metadata(self, pyname):
        """
        Fetch core metadata for a PyPI package.
        
        Returns a dict with name, version, summary, license, etc.
        """
        url = f"https://pypi.org/pypi/{pyname}/json"
        try:
            logger.debug(f"Requesting PyPI metadata from {url}")
            resp = requests.get(url, timeout=self.timeout)
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
        except Exception as e:
            logger.debug(f"Failed to fetch PyPI metadata for {pyname}: {e}")
            raise

    def get_release_info(self, pyname, version):
        """
        Fetch release info (specifically the sdist URL) for a PyPI package version.
        """
        url = f"https://pypi.org/pypi/{pyname}/{version}/json"
        try:
            logger.debug(f"Requesting PyPI release info from {url}")
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # We only care about source distributions (sdist) for PKGBUILDs
            for release in data["urls"]:
                if release["packagetype"] == "sdist":
                    return {"url": release["url"]}
        except Exception as e:
            logger.debug(f"Failed to fetch PyPI release info for {pyname}=={version}: {e}")
        return None

    def verify_existence(self, pyname):
        """
        Check if a package exists on PyPI.
        """
        url = f"https://pypi.org/pypi/{pyname}/json"
        try:
            logger.debug(f"Verifying PyPI existence for {pyname}")
            resp = requests.get(url, timeout=self.timeout)
            return resp.status_code == 200
        except Exception:
            return False

class AURClient:
    def __init__(self, timeout=10):
        """
        Client for interacting with the AUR (Arch User Repository) RPC API and Git.
        """
        self.timeout = timeout

    def get_info(self, pkgname):
        """
        Fetch package info from the AUR RPC v5 API.
        """
        url = f"https://aur.archlinux.org/rpc/v5/info?arg[]={pkgname}"
        try:
            logger.debug(f"Requesting AUR info from {url}")
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if data["resultcount"] > 0:
                return data["results"][0]
        except Exception as e:
            logger.debug(f"Failed to fetch AUR info for {pkgname}: {e}")
        return None

    def clone_repo(self, pkgname, dest_parent):
        """Clone an AUR repository."""
        url = f"https://aur.archlinux.org/{pkgname}.git"
        dest_path = os.path.join(dest_parent, pkgname)
        logger.info(f"Cloning AUR repo {url} to {dest_path}")
        if os.path.exists(dest_path):
            return dest_path
        try:
            run_command(["git", "clone", url, dest_path])
            return dest_path
        except Exception as e:
            logger.error(f"Failed to clone AUR repo for {pkgname}: {e}")
            return None
