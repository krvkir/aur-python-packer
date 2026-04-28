import pytest
from click.testing import CliRunner
from aur_python_packer.cli import cli
from unittest.mock import patch, MagicMock
import networkx as nx

@pytest.fixture
def runner():
    return CliRunner()

@patch('aur_python_packer.cli.Manager')
@patch('aur_python_packer.cli.setup_logging')
def test_cli_build_basic(mock_setup, mock_manager, runner):
    mock_mgr_instance = mock_manager.return_value
    result = runner.invoke(cli, ['-w', 'mywork', 'build', 'python-requests'])
    
    assert result.exit_code == 0
    mock_manager.assert_called_once_with(work_dir='mywork')
    mock_mgr_instance.build_all.assert_called_once_with('python-requests', nocheck=False)

@patch('aur_python_packer.cli.Manager')
@patch('aur_python_packer.cli.setup_logging')
def test_cli_resolve_basic(mock_setup, mock_manager, runner):
    mock_mgr_instance = mock_manager.return_value
    graph = nx.DiGraph()
    graph.add_node("python-requests", tier="repo", version="1.0")
    mock_mgr_instance.resolver.graph = graph
    mock_mgr_instance.resolver.get_build_order.return_value = ["python-requests"]
    
    result = runner.invoke(cli, ['resolve', 'python-requests'])
    
    assert result.exit_code == 0
    assert "Resolving dependencies for python-requests..." in result.output
    mock_mgr_instance.resolver.resolve.assert_called_once_with('python-requests')

@patch('aur_python_packer.cli.Manager')
@patch('aur_python_packer.cli.setup_logging')
def test_cli_cmd(mock_setup, mock_manager, runner):
    mock_mgr_instance = mock_manager.return_value
    result = runner.invoke(cli, ['cmd', 'ls -la'])
    
    assert result.exit_code == 0
    mock_mgr_instance.run_in_sandbox.assert_called_once()
