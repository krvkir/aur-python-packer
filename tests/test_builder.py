import pytest
from unittest.mock import patch, MagicMock
from aur_python_packer.builder import Builder

@patch('os.path.exists')
def test_os_detection_arch(mock_exists):
    # Mocking Arch Linux detection via /etc/arch-release
    mock_exists.side_effect = lambda x: x == "/etc/arch-release"
    orch = Builder()
    assert orch.os_type == "arch"

@patch('aur_python_packer.builder.run_command')
@patch('shutil.which')
@patch('os.path.getmtime')
@patch('glob.glob')
@patch('os.path.abspath')
def test_build_arch(mock_abs, mock_glob, mock_mtime, mock_which, mock_run):
    mock_abs.side_effect = lambda x: x
    mock_glob.return_value = ["/path/to/pkg/test-pkg-1.0.pkg.tar.zst"]
    mock_which.return_value = "/usr/bin/extra-x86_64-build"
    mock_mtime.return_value = 123456789
    orch = Builder()
    orch.os_type = "arch"
    orch.build("test-pkg", "path/to/pkg")
    
    assert mock_run.call_count == 1
    args = mock_run.call_args[0][0]
    assert "extra-x86_64-build" in args
