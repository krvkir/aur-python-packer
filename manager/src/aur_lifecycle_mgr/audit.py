from aur_lifecycle_mgr.generator import PyPIGenerator

class Auditor:
    def __init__(self, state):
        self.state = state
        self.generator = PyPIGenerator()

    def audit(self):
        report = {}
        for pkgname, info in self.state.get("packages", {}).items():
            if pkgname.startswith("python-"):
                pyname = pkgname.replace("python-", "")
                try:
                    latest_meta = self.generator.fetch_meta(pyname)
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
        """Logic to bump version and checksums in PKGBUILD."""
        if not pkgname.startswith("python-"):
            return False
        
        pyname = pkgname.replace("python-", "")
        # Re-generating PKGBUILD with latest info effectively updates it
        self.generator.generate(pyname, directory)
        return True
