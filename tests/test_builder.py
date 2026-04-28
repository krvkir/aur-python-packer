import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock
from aur_python_packer.builder import Builder

@pytest.fixture
def mock_builder_deps():
    with patch("shutil.which") as mock_which, \
         patch("subprocess.run") as mock_run:
        mock_which.side_effect = lambda x: "/usr/bin/bwrap" if x == "bwrap" else None
        mock_run.return_value = MagicMock(returncode=0)
        yield mock_which, mock_run

def test_builder_init(mock_builder_deps):
    builder = Builder(work_dir="/tmp/work")
    assert builder.work_dir == os.path.abspath("/tmp/work")
    assert builder.root_dir == os.path.join(builder.work_dir, "root")

@patch("os.getlogin", return_value="testuser")
@patch("os.getuid", return_value=1000)
@patch("os.getgid", return_value=1000)
@patch("os.makedirs")
@patch("os.chmod")
@patch("builtins.open")
@patch("aur_python_packer.builder.run_command")
@patch("aur_python_packer.builder.Builder._bootstrap_root")
@patch("glob.glob")
@patch("os.path.getmtime")
def test_build(mock_mtime, mock_glob, mock_bootstrap, mock_run_cmd, mock_open, mock_chmod, mock_makedirs, mock_gid, mock_uid, mock_login, mock_builder_deps):
    mock_glob.return_value = ["/tmp/work/pkg.tar.zst"]
    mock_mtime.return_value = 1000
    # Mock open to return a MagicMock for file writing
    mock_open.return_value.__enter__.return_value = MagicMock()
    
    builder = Builder(work_dir="/tmp/work")
    pkg_path = builder.build(
        pkgname="test-pkg",
        directory="/tmp/work/build",
        custom_conf="/tmp/pacman.conf",
        pacman_db_path="/tmp/db"
    )
    
    assert pkg_path == "/tmp/work/pkg.tar.zst"
    mock_bootstrap.assert_called_once()
    # Check if run_command was called (indirectly via _run_in_sandbox)
    assert mock_run_cmd.called
