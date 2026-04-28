import logging
logger = logging.getLogger(__name__)
from aur_python_packer.generator import PyPIGenerator
from aur_python_packer.clients import PyPIClient

class Auditor:
    """
    Audits locally managed packages against upstream versions on PyPI.
    """
    def __init__(self, state):
        self.state = state
        self.generator = PyPIGenerator()
        self.pypi_client = PyPIClient()

    def audit(self):
        """
        Compares current package versions in the state with the latest versions
        available on PyPI.
        """
        logger.info("Auditing managed packages against PyPI...")
        report = {}
        for pkgname, info in self.state.get("packages", {}).items():
            if pkgname.startswith("python-"):
                pyname = pkgname.replace("python-", "")
                try:
                    latest_meta = self.pypi_client.get_metadata(pyname)
                    latest_ver = latest_meta["version"]
                    current_ver = info["version"]
                    
                    report[pkgname] = {
                        "current": current_ver,
                        "latest": latest_ver,
                        "outdated": current_ver != latest_ver
                    }
                except Exception:
                    continue
        return report

    def update_package(self, pkgname, directory):
        """
        Updates a package to its latest PyPI version by regenerating its PKGBUILD.
        """
        logger.info(f"Triggering update for {pkgname} in {directory}")
        if not pkgname.startswith("python-"):
            return False
        
        pyname = pkgname.replace("python-", "")
        # Re-generating the PKGBUILD with latest metadata effectively performs the update.
        self.generator.generate(pyname, directory)
        return True
