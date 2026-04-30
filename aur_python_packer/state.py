import json
import os
from datetime import datetime

class StateManager:
    def __init__(self, state_file="build_index.json"):
        self.state_file = state_file
        self.state = self._load()

    def _load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {"packages": {}, "last_run": None}

    def save(self):
        self.state["last_run"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=4)

    def update_package(self, pkgname, version, status, skipped_checks=False):
        self.state["packages"][pkgname] = {
            "version": version,
            "status": status,
            "last_build": datetime.now().isoformat(),
            "skipped_checks": skipped_checks
        }
        self.save()

    def get_package(self, pkgname):
        return self.state["packages"].get(pkgname)
