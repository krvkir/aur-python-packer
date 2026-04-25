import os
import shutil
import subprocess

class RepoManager:
    def __init__(self, repo_dir, db_name="localrepo"):
        self.repo_dir = os.path.abspath(repo_dir)
        self.db_name = db_name
        self.db_path = os.path.join(self.repo_dir, f"{db_name}.db.tar.gz")
        os.makedirs(self.repo_dir, exist_ok=True)

    def add_package(self, pkg_path):
        pkg_name = os.path.basename(pkg_path)
        dest_path = os.path.join(self.repo_dir, pkg_name)
        shutil.copy2(pkg_path, dest_path)
        
        # Update repo db
        subprocess.run(
            ['repo-add', self.db_path, dest_path],
            check=True,
            capture_output=True
        )

    def get_pacman_conf_fragment(self):
        return f"""
[{self.db_name}]
SigLevel = Optional TrustAll
Server = file://{self.repo_dir}
"""

    def inject_into_conf(self, conf_path):
        with open(conf_path, 'r') as f:
            content = f.read()
        
        if f"[{self.db_name}]" not in content:
            with open(conf_path, 'a') as f:
                f.write(self.get_pacman_conf_fragment())
