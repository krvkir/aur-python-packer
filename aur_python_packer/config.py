import os
import logging

logger = logging.getLogger(__name__)

class PacmanConfig:
    """
    Handles generation and patching of pacman.conf files.
    """
    def __init__(self, repo_dir, db_name="localrepo", db_path_override=None, cache_path_override=None, log_path_override=None, gpg_dir_override=None):
        """
        Initializes the config manager with paths for the custom repository and pacman overrides.
        """
        self.repo_dir = os.path.abspath(repo_dir)
        self.db_name = db_name
        self.db_path_override = db_path_override
        self.cache_path_override = cache_path_override
        self.log_path_override = log_path_override
        self.gpg_dir_override = gpg_dir_override

    def generate(self, base_conf="/etc/pacman.conf", output_path="pacman.conf"):
        """
        Generates a custom pacman.conf by patching a base configuration.
        
        Overrides core options like DBPath and CacheDir, and appends the 
        local repository section.
        """
        logger.debug(f"Generating custom pacman.conf from {base_conf} to {output_path}")
        with open(base_conf, 'r') as f:
            content = f.read()
        
        new_lines = []
        # Filter out existing options that we want to override
        for line in content.splitlines():
            stripped = line.strip()
            if (stripped.startswith("DBPath") or stripped.startswith("CacheDir") or 
                stripped.startswith("SigLevel") or stripped.startswith("LocalFileSigLevel") or
                stripped.startswith("XferCommand")):
                continue
            # Remove existing [options] header as we re-insert it with our overrides
            if stripped == "[options]":
                continue
            new_lines.append(line)

        overrides = ["[options]"]
        # Ensure signatures are not required for our local unsigned repo
        overrides.append("SigLevel = Never")
        overrides.append("LocalFileSigLevel = Never")
        
        # Explicitly set XferCommand to bypass pacman 7.1's DownloadUser logic
        # which often fails in rootless containers due to permission issues with 'alpm' user.
        overrides.append('XferCommand = /usr/bin/curl -L -C - -f -o %o %u')

        # Apply custom paths if provided
        if self.db_path_override:
            overrides.append(f"DBPath = {self.db_path_override}")
        
        if self.cache_path_override:
            overrides.append(f"CacheDir = {self.cache_path_override}")

        if self.log_path_override:
            overrides.append(f"LogFile = {self.log_path_override}")

        if self.gpg_dir_override:
            overrides.append(f"GPGDir = {self.gpg_dir_override}")

        with open(output_path, 'w') as f:
            f.write("\n".join(overrides) + "\n")
            f.write("\n".join(new_lines) + "\n")
            # Append the local repository section
            f.write(f"\n[{self.db_name}]\n")
            f.write("SigLevel = Optional TrustAll\n")
            f.write(f"Server = file://{self.repo_dir}\n")
        
        return os.path.abspath(output_path)
