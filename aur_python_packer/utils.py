import logging
import os
import subprocess
from dataclasses import dataclass


@dataclass
class CommandResult:
    stdout: str
    returncode: int


logger = logging.getLogger(__name__)


def run_command(cmd, cwd=None, env=None, check=True, log_level=logging.DEBUG, msg=None):
    """
    Executes a command, logs its merged output (stdout/stderr) in real-time.
    Logs the command and any environment overrides at DEBUG level.
    """
    if msg:
        logger.info(msg)
    logger.debug(f"Executing command: {' '.join(cmd)}")
    effective_cwd = cwd if cwd else os.getcwd()
    logger.debug(f"CWD: {effective_cwd}")
    if env:
        # Only log differences/overrides if we were to compare with os.environ,
        # but here we just log what's passed in 'env' as requested.
        logger.debug(f"Env overrides: {env}")

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    output_lines = []
    for line in process.stdout:
        stripped_line = line.rstrip()
        logger.log(log_level, stripped_line)
        output_lines.append(stripped_line)

    return_code = process.wait()

    if check and return_code != 0:
        last_output = "\n".join(output_lines[-20:])
        error_msg = (
            f"Command '{' '.join(cmd)}' failed with exit code {return_code}.\n"
            f"Last output:\n{last_output}"
        )
        logger.error(error_msg)
        # Raise exception similar to subprocess.run(check=True)
        raise subprocess.CalledProcessError(
            returncode=return_code, cmd=cmd, output="\n".join(output_lines)
        )

    return CommandResult(stdout="\n".join(output_lines), returncode=return_code)


def get_git_identity():
    """
    Returns a string "Name <email>" from git config --global user.name and user.email.
    Fallback to "AUR Packer <aur-packer@localhost>".
    """
    name = "AUR Packer"
    email = "aur-packer@localhost"

    try:
        res_name = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res_name.returncode == 0 and res_name.stdout.strip():
            name = res_name.stdout.strip()

        res_email = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res_email.returncode == 0 and res_email.stdout.strip():
            email = res_email.stdout.strip()
    except Exception as e:
        logger.debug(f"Failed to fetch host git identity: {e}")

    return f"{name} <{email}>"
