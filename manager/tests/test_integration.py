import pytest
from unittest.mock import patch, MagicMock
from aur_lifecycle_mgr.main import Manager

@patch('aur_lifecycle_mgr.resolver.DependencyResolver.resolve')
@patch('aur_lifecycle_mgr.resolver.DependencyResolver.get_build_order')
@patch('aur_lifecycle_mgr.builder.BuildOrchestrator.build')
@patch('aur_lifecycle_mgr.repo.RepoManager.add_package')
def test_full_cycle(mock_add, mock_build, mock_order, mock_resolve, tmp_path):
    mock_order.return_value = ["dep1", "target"]
    mock_build.return_value = "target-1.0.pkg.tar.zst"
    
    # Mocking build_state.json path
    state_file = tmp_path / "state.json"
    
    mgr = Manager(state_file=str(state_file), repo_dir=str(tmp_path / "repo"))
    # Manually add nodes to graph since resolve is mocked
    mgr.resolver.graph.add_node("dep1", tier="repo")
    mgr.resolver.graph.add_node("target", tier="local", path=".")
    
    mgr.build_all("target")
    
    assert mock_resolve.called
    assert mock_build.call_count == 1 # dep1 is repo tier, so only 1 build
    assert mock_add.call_count == 1
