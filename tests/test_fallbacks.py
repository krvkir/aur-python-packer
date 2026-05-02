import pytest
import os
from unittest.mock import patch, MagicMock
from aur_python_packer.main import Manager

@patch('aur_python_packer.resolver.DependencyResolver.resolve')
@patch('aur_python_packer.resolver.DependencyResolver.get_build_order')
@patch('aur_python_packer.builder.Builder.build')
@patch('aur_python_packer.repo.RepoManager.add_package')
@patch('aur_python_packer.builder.Builder._bootstrap_root')
@patch('aur_python_packer.repo.RepoManager.generate_custom_conf')
def test_build_fallback(mock_conf, mock_bootstrap, mock_add, mock_build, mock_order, mock_resolve, tmp_path):
    # Setup
    mgr = Manager(work_dir=str(tmp_path))
    mock_order.return_value = ["pkg1"]
    mgr.resolver.graph.add_node("pkg1", tier="local", path=".", version="1.0")
    mock_conf.return_value = "/tmp/pacman.conf"
    
    # Mock first call to fail, second to succeed
    mock_build.side_effect = [Exception("Build failed"), "pkg1-1.0.pkg.tar.zst"]
    mgr._sync_pacman = MagicMock()

    # Execute
    mgr.build_all("pkg1")
    
    # Verify
    assert mock_build.call_count == 2
    # First call: nocheck=False (default)
    assert mock_build.call_args_list[0].kwargs['nocheck'] is False
    # Second call: nocheck=True
    assert mock_build.call_args_list[1].kwargs['nocheck'] is True
    
    # Verify state
    pkg_state = mgr.state.get_package("pkg1")
    assert pkg_state['status'] == "success"
    assert pkg_state['skipped_checks'] is True

@patch('aur_python_packer.resolver.DependencyResolver.resolve')
@patch('aur_python_packer.resolver.DependencyResolver.get_build_order')
@patch('aur_python_packer.builder.Builder.build')
@patch('aur_python_packer.repo.RepoManager.add_package')
@patch('aur_python_packer.builder.Builder._bootstrap_root')
@patch('aur_python_packer.repo.RepoManager.generate_custom_conf')
def test_build_nocheck_global(mock_conf, mock_bootstrap, mock_add, mock_build, mock_order, mock_resolve, tmp_path):
    # Setup
    mgr = Manager(work_dir=str(tmp_path))
    mock_order.return_value = ["pkg1"]
    mgr.resolver.graph.add_node("pkg1", tier="local", path=".", version="1.0")
    mock_conf.return_value = "/tmp/pacman.conf"
    
    mock_build.return_value = "pkg1-1.0.pkg.tar.zst"
    mgr._sync_pacman = MagicMock()

    # Execute with global nocheck
    mgr.build_all("pkg1", nocheck=True)
    
    # Verify
    assert mock_build.call_count == 1
    assert mock_build.call_args.kwargs['nocheck'] is True
    
    # Verify state
    pkg_state = mgr.state.get_package("pkg1")
    assert pkg_state['status'] == "success"
    assert pkg_state['skipped_checks'] is True

@patch('aur_python_packer.resolver.DependencyResolver.resolve')
@patch('aur_python_packer.resolver.DependencyResolver.get_build_order')
@patch('aur_python_packer.builder.Builder.build')
@patch('aur_python_packer.repo.RepoManager.add_package')
@patch('aur_python_packer.builder.Builder._bootstrap_root')
@patch('aur_python_packer.repo.RepoManager.generate_custom_conf')
def test_build_total_failure(mock_conf, mock_bootstrap, mock_add, mock_build, mock_order, mock_resolve, tmp_path):
    # Setup
    mgr = Manager(work_dir=str(tmp_path))
    mock_order.return_value = ["pkg1"]
    mgr.resolver.graph.add_node("pkg1", tier="local", path=".", version="1.0")
    mock_conf.return_value = "/tmp/pacman.conf"
    
    # Mock both calls to fail
    mock_build.side_effect = Exception("Build failed")
    mgr._sync_pacman = MagicMock()

    # Execute
    mgr.build_all("pkg1")
    
    # Verify
    assert mock_build.call_count == 2
    
    # Verify state
    pkg_state = mgr.state.get_package("pkg1")
    assert pkg_state['status'] == "failed"
