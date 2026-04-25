import pytest
from unittest.mock import patch, MagicMock
from aur_lifecycle_mgr.builder import BuildOrchestrator

@patch('os.path.exists')
def test_os_detection_arch(mock_exists):
    # Mocking Arch Linux detection via /etc/arch-release
    mock_exists.side_effect = lambda x: x == "/etc/arch-release"
    orch = BuildOrchestrator()
    assert orch.get_os() == "arch"

@patch('subprocess.run')
@patch('glob.glob')
def test_build_arch(mock_glob, mock_run):
    mock_glob.return_value = ["/path/to/pkg/test-pkg-1.0.pkg.tar.zst"]
    orch = BuildOrchestrator()
    orch.os_type = "arch"
    orch.build("test-pkg", "path/to/pkg")
    
    assert mock_run.call_count == 2
    # Check that the second call was the actual build command
    args = mock_run.call_args_list[1][0][0]
    assert "extra-x86_64-build" in args
