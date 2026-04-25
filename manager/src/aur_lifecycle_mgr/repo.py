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

    def generate_custom_conf(self, base_conf="/etc/pacman.conf", output_path="pacman.conf"):
        with open(base_conf, 'r') as f:
            lines = f.readlines()
        
        # We need to find where [options] section is to add our repo?
        # Actually, adding it at the end is fine, but we should make sure
        # our repo has higher priority if needed.
        
        with open(output_path, 'w') as f:
            for line in lines:
                f.write(line)
            f.write(self.get_pacman_conf_fragment())
        return os.path.abspath(output_path)
