import pytest
from click.testing import CliRunner
from aur_python_packer.cli import cli
from unittest.mock import patch, MagicMock
import networkx as nx


@pytest.fixture
def runner():
    return CliRunner()


@patch("aur_python_packer.cli.Manager")
@patch("aur_python_packer.cli.setup_logging")
def test_cli_build_basic(mock_setup, mock_manager, runner):
    mock_mgr_instance = mock_manager.return_value
    result = runner.invoke(cli, ["-w", "mywork", "build", "python-requests"])

    assert result.exit_code == 0
    mock_manager.assert_called_once_with(work_dir="mywork")
    mock_mgr_instance.build_all.assert_called_once_with(
        "python-requests", nocheck=False, inject_depends=[]
    )


@patch("aur_python_packer.cli.Manager")
@patch("aur_python_packer.cli.setup_logging")
def test_cli_resolve_basic(mock_setup, mock_manager, runner):
    mock_mgr_instance = mock_manager.return_value
    graph = nx.DiGraph()
    graph.add_node("python-requests", tier="repo", version="1.0")
    mock_mgr_instance.resolver.graph = graph
    mock_mgr_instance.resolver.get_build_order.return_value = ["python-requests"]

    result = runner.invoke(cli, ["resolve", "python-requests"])

    assert result.exit_code == 0
    assert "Resolving dependencies for python-requests..." in result.output
    mock_mgr_instance.resolver.resolve.assert_called_once_with("python-requests")


@patch("aur_python_packer.cli.Manager")
@patch("aur_python_packer.cli.setup_logging")
def test_cli_cmd(mock_setup, mock_manager, runner):
    mock_mgr_instance = mock_manager.return_value
    result = runner.invoke(cli, ["cmd", "ls -la"])

    assert result.exit_code == 0
    mock_mgr_instance.run_in_sandbox.assert_called_once()


@patch("aur_python_packer.cli.Manager")
@patch("aur_python_packer.cli.setup_logging")
def test_cli_git_init(mock_setup, mock_manager, runner):
    """git-init command calls Manager.git_init_all()."""
    mock_mgr_instance = mock_manager.return_value
    result = runner.invoke(cli, ["git-init"])

    assert result.exit_code == 0
    mock_manager.assert_called_once()
    mock_mgr_instance.git_init_all.assert_called_once()
    assert "Git repositories initialized." in result.output


@patch("aur_python_packer.cli.Manager")
@patch("aur_python_packer.cli.setup_logging")
def test_cli_git_show_with_changes(mock_setup, mock_manager, runner):
    """git-show lists packages with uncommitted changes."""
    mock_mgr_instance = mock_manager.return_value
    mock_mgr_instance.git_show_changed.return_value = ["python-foo", "python-bar"]

    result = runner.invoke(cli, ["git-show"])

    assert result.exit_code == 0
    mock_mgr_instance.git_show_changed.assert_called_once()
    assert "python-foo" in result.output
    assert "python-bar" in result.output


@patch("aur_python_packer.cli.Manager")
@patch("aur_python_packer.cli.setup_logging")
def test_cli_git_show_no_changes(mock_setup, mock_manager, runner):
    """git-show reports clean state."""
    mock_mgr_instance = mock_manager.return_value
    mock_mgr_instance.git_show_changed.return_value = []

    result = runner.invoke(cli, ["git-show"])

    assert result.exit_code == 0
    assert "No packages with uncommitted changes." in result.output


@patch("aur_python_packer.cli.Manager")
@patch("aur_python_packer.cli.setup_logging")
def test_cli_build_with_depends(mock_setup, mock_manager, runner):
    """build --depends passes injected dependencies to build_all."""
    mock_mgr_instance = mock_manager.return_value
    result = runner.invoke(
        cli,
        ["-w", "mywork", "build", "python-foo", "-d", "python-bar", "-d", "python-baz"],
    )

    assert result.exit_code == 0
    mock_mgr_instance.build_all.assert_called_once_with(
        "python-foo", nocheck=False, inject_depends=["python-bar", "python-baz"]
    )


@patch("aur_python_packer.cli.Manager")
@patch("aur_python_packer.cli.setup_logging")
def test_cli_build_with_single_depends(mock_setup, mock_manager, runner):
    """build with a single --depends value works."""
    mock_mgr_instance = mock_manager.return_value
    result = runner.invoke(cli, ["build", "python-foo", "-d", "python-bar"])

    assert result.exit_code == 0
    mock_mgr_instance.build_all.assert_called_once_with(
        "python-foo", nocheck=False, inject_depends=["python-bar"]
    )
