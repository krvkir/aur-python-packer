import logging
import os
import shutil

from aur_python_packer.utils import run_command

logger = logging.getLogger(__name__)


class Sandbox:
    """
    Manages execution isolation using Bubblewrap (bwrap).
    Handles bind mounts, user namespaces, and shim generation.
    """

    def __init__(self, work_dir, root_dir):
        self.work_dir = os.path.abspath(work_dir)
        self.root_dir = os.path.abspath(root_dir)
        self.srv_dir = os.path.join(self.work_dir, "srv")
        self.bin_dir = os.path.join(self.srv_dir, "bin")
        self.etc_dir = os.path.join(self.srv_dir, "etc")

    def get_bwrap_command(self, cmd, cwd, custom_conf, pacman_db_path, share_net=False):
        """
        Constructs the full bwrap command list with necessary binds and env vars.
        """
        logger.debug(f"Constructing bwrap command for: {cmd}")

        # We map the current user to themselves (not root) to satisfy makepkg
        # Root operations for pacman will be handled via the sudo shim + fakeroot
        uid = os.getuid()
        gid = os.getgid()
        username = os.getlogin()
        home_dir = os.path.join(self.srv_dir, "home", username)
        os.makedirs(home_dir, exist_ok=True)

        nproc = os.cpu_count() or 1
        passwd_path = os.path.join(self.etc_dir, "passwd")
        group_path = os.path.join(self.etc_dir, "group")

        # fmt: off
        # Core isolation flags: unshare user namespace, map current user to same UID/GID
        # bind-mount the root filesystem (bootstrapped earlier)
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
            # Point pacman's local DB to the one we manage (which includes host's /var/lib/pacman/local)
            # This allows finding official repo packages without having them installed in root_dir.
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
        # fmt: on

        # Optional networking (required for updpkgsums to download sources)
        if share_net:
            bwrap_cmd.append("--share-net")

        if not cwd.startswith(self.work_dir):
            bwrap_cmd.extend(["--bind", cwd, cwd])

        bwrap_cmd.extend(cmd)
        return bwrap_cmd

    def run(
        self,
        cmd,
        cwd,
        custom_conf,
        pacman_db_path,
        log_level=logging.DEBUG,
        check=True,
        share_net=False,
    ):
        bwrap_cmd = self.get_bwrap_command(
            cmd, cwd, custom_conf, pacman_db_path, share_net=share_net
        )
        summary = f"[Sandbox{': shared-net' if share_net else ''}] {' '.join(cmd)}"
        return run_command(bwrap_cmd, log_level=log_level, check=check, msg=summary)

    def run_host_command(self, cmd, log_level=logging.DEBUG, check=True):
        """
        Run a command using host tools but in a fake-root user namespace.
        Useful for bootstrapping or syncing databases where we want to use host's pacman
        but modify files in the work_dir/sandbox without root privileges.
        """
        # fmt: off
        os.makedirs(self.root_dir, exist_ok=True)
        bwrap_cmd = [
            "bwrap",
            "--unshare-user",
            "--uid", "0",
            "--gid", "0",
            "--bind", "/", "/",
            "--dev", "/dev",
            "--proc", "/proc",
            "--bind", self.work_dir, self.work_dir,
            "--bind", self.root_dir, self.root_dir,
        ]
        # fmt: on
        bwrap_cmd.extend(cmd)
        summary = f"[Host-root] {' '.join(cmd)}"
        return run_command(bwrap_cmd, log_level=log_level, check=check, msg=summary)

    def generate_shims(self, custom_conf, pacman_db_path):
        """
        Generates sudo and pacman shell shims.

        These shims intercept calls from tools like makepkg and redirect them
        to use the custom pacman configuration and database path, enabling
        rootless dependency installation and checking.
        """
        logger.debug("Generating shell shims for sandbox")
        os.makedirs(self.bin_dir, exist_ok=True)
        os.makedirs(self.etc_dir, exist_ok=True)

        sudo_shim_path = os.path.join(self.bin_dir, "sudo")
        pacman_shim_path = os.path.join(self.bin_dir, "pacman")

        self._write_passwd_group()

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
            f.write("        pacman|*/pacman)\n")
            f.write('            while [ "$1" != "$arg" ]; do shift; done\n')
            f.write("            shift\n")
            f.write(f'            exec {pacman_base} "$@"\n')
            f.write("            ;;\n")
            f.write("    esac\n")
            f.write("done\n")
            f.write('if [ "$1" = "--" ]; then shift; fi\n')
            f.write('exec "$@"\n')

        # Pacman shim: ensures non-sudo pacman calls (like makepkg's pacman -T) also use the custom DB.
        with open(pacman_shim_path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write(
                f'exec /usr/bin/pacman --config "{custom_conf}" --dbpath "{pacman_db_path}" "$@"\n'
            )

        os.chmod(sudo_shim_path, 0o755)
        os.chmod(pacman_shim_path, 0o755)

    def _write_passwd_group(self):
        """
        Writes custom /etc/passwd and /etc/group files into the workspace.
        These are bind-mounted into the sandbox to provide correct user/group info
        for tools like makepkg and pacman.
        """
        passwd_path = os.path.join(self.etc_dir, "passwd")
        group_path = os.path.join(self.etc_dir, "group")

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
