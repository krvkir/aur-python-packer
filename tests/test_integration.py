import pytest
import os
from unittest.mock import patch, MagicMock
from aur_python_packer.main import Manager

@patch('aur_python_packer.resolver.DependencyResolver.resolve')
@patch('aur_python_packer.resolver.DependencyResolver.get_build_order')
@patch('aur_python_packer.builder.Builder.build')
@patch('aur_python_packer.repo.RepoManager.add_package')
@patch('aur_python_packer.sandbox.Sandbox.run_host_command')
@patch('aur_python_packer.builder.Builder._bootstrap_root')
def test_full_cycle(mock_bootstrap, mock_run_host, mock_add, mock_build, mock_order, mock_resolve, tmp_path):
    mock_order.return_value = ["dep1", "target"]
    mock_build.return_value = "target-1.0.pkg.tar.zst"
    
    mgr = Manager(work_dir=str(tmp_path))
    # Manually add nodes to graph since resolve is mocked
    mgr.resolver.graph.add_node("dep1", tier="repo")
    mgr.resolver.graph.add_node("target", tier="local", path=".")
    
    mgr.build_all("target")
    
    assert mock_resolve.called
    assert mock_build.call_count == 1 # dep1 is repo tier, so only 1 build
    assert mock_add.call_count == 1

    # Verify state file was created
    assert os.path.exists(os.path.join(tmp_path, "srv", "build_index.json"))
