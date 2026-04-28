import glob
import os
import logging
import shutil
import subprocess

from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)

class Builder:
    def __init__(self, work_dir):
        self.work_dir = os.path.abspath(work_dir)
        self.root_dir = os.path.join(self.work_dir, "root")
        self.bin_dir = os.path.join(self.work_dir, "bin")
        self._check_dependencies()

    def _check_dependencies(self):
        if not shutil.which("bwrap"):
            raise RuntimeError("bubblewrap (bwrap) is required for rootless builds.")
        
        # Check for unprivileged user namespace support
        try:
            subprocess.run(["unshare", "--user", "true"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Unprivileged user namespaces are not supported or disabled. "
                "Ensure /proc/sys/kernel/unprivileged_userns_clone is 1 (on some distros) "
                "or your kernel supports them."
            )

    def _bootstrap_root(self, custom_conf, pacman_db_path):
        # Check if root is already bootstrapped with fakeroot
        if os.path.exists(os.path.join(self.root_dir, "usr/bin/fakeroot")):
             return

        logger.info(f"Bootstrapping minimal root at {self.root_dir} (this may take a while)...")
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(os.path.join(self.root_dir, "var/lib/pacman"), exist_ok=True)
        
        # Copy host's pacman.conf to root to ensure same repositories are available
        # Actually, Manager.build_all uses custom_conf which is based on host's conf.
        # But for other tools in the sandbox, having a good /etc/pacman.conf is helpful.
        host_conf = "/etc/pacman.conf"
        target_conf = os.path.join(self.root_dir, "etc/pacman.conf")
        if os.path.exists(host_conf):
             os.makedirs(os.path.dirname(target_conf), exist_ok=True)
             shutil.copy2(host_conf, target_conf)

        # Use pacman --root with bwrap to install base-devel into the directory
        # We use a separate dbpath to ensure we don't conflict with the host's or the custom DB.
        cmd = [
            "bwrap", "--unshare-user", "--uid", "0", "--gid", "0",
            "--bind", "/", "/",
            "--dev", "/dev",
            "--proc", "/proc",
            "--bind", self.work_dir, self.work_dir,
            "pacman", "-Sy",
            "base-devel", "pacman", "python", "git", "bubblewrap", "util-linux", "bash", "curl", "fakeroot",
            "ca-certificates", "ca-certificates-utils",
            "python-build", "python-installer", "python-setuptools", "python-wheel",
            "python-hatchling", "python-flit-core", "python-poetry-core", "python-setuptools-scm",
            "python-editables", "python-pathspec", "python-pluggy", "python-trove-classifiers",
            "python-dunamai", "python-pydantic", "python-pydantic-core", "python-anyio",
            "python-starlette", "python-httpx", "python-rich", "python-typing_extensions",
            "--noconfirm", "--needed",
            "--root", self.root_dir,
            "--config", "/etc/pacman.conf",
        ]
        # Use higher log level for bootstrap as it's a major operation
        run_command(cmd, log_level=logging.INFO)

    def _generate_sudo_shim(self, custom_conf, pacman_db_path):
        os.makedirs(self.bin_dir, exist_ok=True)
        sudo_shim_path = os.path.join(self.bin_dir, "sudo")
        pacman_shim_path = os.path.join(self.bin_dir, "pacman")
        
        # Create a persistent passwd/group in work dir that contains alpm and the user
        etc_dir = os.path.join(self.work_dir, "etc")
        os.makedirs(etc_dir, exist_ok=True)
        passwd_path = os.path.join(etc_dir, "passwd")
        group_path = os.path.join(etc_dir, "group")
        
        uid = os.getuid()
        gid = os.getgid()
        username = os.getlogin()

        with open(passwd_path, "w") as f:
            f.write("root:x:0:0::/root:/usr/bin/bash\n")
            f.write("alpm:x:973:973:Arch Linux Package Management:/:/usr/bin/nologin\n")
            f.write("nobody:x:65534:65534:Nobody:/:/usr/bin/nologin\n")
            f.write(f"{username}:x:{uid}:{gid}::/home/{username}:/usr/bin/bash\n")
            
        with open(group_path, "w") as f:
            f.write("root:x:0:root\n")
            f.write("alpm:x:973:\n")
            f.write("nobody:x:65534:\n")
            f.write(f"{username}:x:{gid}:\n")

        # Sandbox command for pacman (run as root)
        # We use fakeroot to trick pacman into thinking it's root.
        # Since we are already in a user namespace and the files are owned by us, 
        # this is enough to perform operations on the local DB and root.
        pacman_base = f'fakeroot /usr/bin/pacman --config "{custom_conf}" --dbpath "{pacman_db_path}"'

        # Sudo shim: robustly finds 'pacman' in arguments and injects bwrap.
        with open(sudo_shim_path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write('for arg in "$@"; do\n')
            f.write('    case "$arg" in\n')
            f.write('        pacman|*/pacman)\n')
            f.write('            while [ "$1" != "$arg" ]; do shift; done\n')
            f.write('            shift\n')
            f.write(f'            exec {pacman_base} "$@"\n')
            f.write('            ;;\n')
            f.write('    esac\n')
            f.write('done\n')
            f.write('if [ "$1" = "--" ]; then shift; fi\n')
            f.write('exec "$@"\n')
        
        # Pacman shim: ensures non-sudo pacman calls (like makepkg's pacman -T) also use the custom DB.
        with open(pacman_shim_path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write(f'exec /usr/bin/pacman --config "{custom_conf}" --dbpath "{pacman_db_path}" "$@"\n')

        os.chmod(sudo_shim_path, 0o755)
        os.chmod(pacman_shim_path, 0o755)
        return sudo_shim_path


    def _run_in_sandbox(self, cmd, cwd, custom_conf, pacman_db_path):
        etc_dir = os.path.join(self.work_dir, "etc")
        passwd_path = os.path.join(etc_dir, "passwd")
        group_path = os.path.join(etc_dir, "group")
        
        # Get current user IDs
        uid = os.getuid()
        gid = os.getgid()
        username = os.getlogin()
        
        # Ensure home directory exists in work dir
        home_dir = os.path.join(self.work_dir, "home", username)
        os.makedirs(home_dir, exist_ok=True)

        # Generate shims (sudo and pacman)
        self._generate_sudo_shim(custom_conf, pacman_db_path)

        # bwrap command construction
        nproc = os.cpu_count() or 1
        # We map the current user to themselves (not root) to satisfy makepkg
        # Root operations for pacman will be handled via the sudo shim + fakeroot
        bwrap_cmd = [
            "bwrap",
            "--unshare-user",
            "--uid", str(uid),
            "--gid", str(gid),
            "--bind", self.root_dir, "/",
            "--dev", "/dev",
            "--proc", "/proc",
            "--tmpfs", "/tmp",
            "--bind", self.work_dir, self.work_dir,
            "--bind", os.path.join(self.root_dir, "var/lib/pacman/local"), os.path.join(pacman_db_path, "local"),
            "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
            "--ro-bind", "/etc/pacman.d", "/etc/pacman.d",
            "--ro-bind", "/etc/ssl/certs", "/etc/ssl/certs",
            "--ro-bind", "/etc/ca-certificates", "/etc/ca-certificates",
            "--ro-bind", "/etc/hosts", "/etc/hosts",
            "--ro-bind", "/etc/nsswitch.conf", "/etc/nsswitch.conf",
            "--ro-bind", passwd_path, "/etc/passwd",
            "--ro-bind", group_path, "/etc/group",
            "--bind", home_dir, f"/home/{username}",
            "--setenv", "PATH", f"{self.bin_dir}:/usr/bin",
            "--setenv", "HOME", f"/home/{username}",
            "--setenv", "PACKAGER", "AUR Python Packer <aur-python-packer@localhost>",
            "--setenv", "MAKEFLAGS", f"-j{nproc}",
            "--chdir", cwd
        ]
        
        # Also bind-mount the directory being built if it's outside work_dir
        if not cwd.startswith(self.work_dir):
             bwrap_cmd.extend(["--bind", cwd, cwd])

        logger.debug(f"Sandbox CWD: {cwd}")
        logger.debug(f"Sandbox PATH: {self.bin_dir}:/usr/bin")
        bwrap_cmd.extend(cmd)

        run_command(bwrap_cmd)

    def build(self, pkgname, directory, deps=None, nocheck=False, custom_conf=None, pacman_db_path=None):
        directory = os.path.abspath(directory)
        
        if not custom_conf:
            raise ValueError("custom_conf is required for rootless builds")

        self._bootstrap_root(custom_conf, pacman_db_path)
        return self.execute_sandboxed_build(pkgname, directory, deps, nocheck, custom_conf, pacman_db_path)

    def execute_sandboxed_build(self, pkgname, directory, deps, nocheck, custom_conf, pacman_db_path):
        # Build command for makepkg
        # We use -s to install dependencies, which will use our sudo shim
        cmd = ["makepkg", "-s", "-f", "--noconfirm", "--skippgpcheck"]
        if nocheck:
            cmd.append("--nocheck")

        logger.info(f"Starting sandboxed build for {pkgname}...")
        # Ensure the build user can write to the directory
        # In the sandbox we are root (uid 0), and we mapped our current user to uid 0.
        # So we should have permission.
        
        # For first-time builds, makepkg -s might fail if repos are not synced.
        # We rely on Manager having done the sync, but inside the sandbox
        # we might need to ensure the DBPath is reachable.

        self._run_in_sandbox(cmd, cwd=directory, custom_conf=custom_conf, pacman_db_path=pacman_db_path)
        logger.info(f"Successfully finished building {pkgname}")
        return self._find_package_file(directory)

    def _find_package_file(self, directory):
        pkg_files = glob.glob(os.path.join(directory, "*.pkg.tar.zst"))
        if not pkg_files:
            raise FileNotFoundError(
                f"Build finished but no package file found in {directory}"
            )
        return max(pkg_files, key=os.path.getmtime)
