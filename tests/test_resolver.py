import pytest
from unittest.mock import patch, MagicMock, call
from aur_python_packer.resolver import DependencyResolver


def test_topological_sort_linear():
    resolver = DependencyResolver()
    resolver.graph.add_edge("A", "B")  # A depends on B
    assert resolver.get_build_order() == ["B", "A"]


def test_topological_sort_diamond():
    resolver = DependencyResolver()
    resolver.graph.add_edge("A", "B")
    resolver.graph.add_edge("A", "C")
    resolver.graph.add_edge("B", "D")
    resolver.graph.add_edge("C", "D")
    order = resolver.get_build_order()
    assert order.index("D") < order.index("B")
    assert order.index("D") < order.index("C")
    assert order.index("B") < order.index("A")
    assert order.index("C") < order.index("A")


def test_circular_dependency():
    resolver = DependencyResolver()
    resolver.graph.add_edge("A", "B")
    resolver.graph.add_edge("B", "A")
    with pytest.raises(ValueError, match="Circular dependency detected"):
        resolver.get_build_order()


@patch("aur_python_packer.resolver.find_provider_in_repos")
@patch("aur_python_packer.clients.AURClient.get_info")
@patch("aur_python_packer.resolver.DependencyResolver._find_in_dir")
@patch("aur_python_packer.clients.AURClient.clone_repo")
def test_resolve_cascade(mock_clone, mock_find_in_dir, mock_aur, mock_repo):
    # Setup mocks
    mock_find_in_dir.return_value = None  # No local
    mock_repo.side_effect = (
        lambda x: x if x == "pacman" else None
    )  # pacman is in repo
    mock_aur.side_effect = (
        lambda x: {"Depends": ["pacman"], "Version": "1.0"}
        if x == "aur-pkg"
        else None
    )
    mock_clone.return_value = "aur_packages/aur-pkg"

    # Calls to find_in_dir:
    # 1. packages/aur-pkg
    # 2. aur_packages/aur-pkg (initial check)
    # 3. aur_packages/aur-pkg (after clone check)
    # 4. packages/pacman (when resolving dependency)
    mock_find_in_dir.side_effect = [
        None,
        None,
        {"path": "aur_packages/aur-pkg", "depends": ["pacman"], "version": "1.0"},
        None,
    ]

    resolver = DependencyResolver(work_dir="work")
    resolver.resolve("aur-pkg")

    assert "aur-pkg" in resolver.graph.nodes
    assert resolver.graph.nodes["aur-pkg"]["tier"] == "aur"
    assert "pacman" in resolver.graph.nodes
    assert resolver.graph.nodes["pacman"]["tier"] == "repo"
    assert ("aur-pkg", "pacman") in resolver.graph.edges
    assert resolver.get_build_order() == ["pacman", "aur-pkg"]


@patch("aur_python_packer.clients.PyPIClient.verify_existence")
@patch("aur_python_packer.resolver.DependencyResolver.pypi_get_dependencies")
@patch("aur_python_packer.clients.PyPIClient.get_metadata")
@patch("aur_python_packer.resolver.find_provider_in_repos")
@patch("aur_python_packer.clients.AURClient.get_info")
@patch("aur_python_packer.resolver.DependencyResolver._find_in_dir")
def test_resolve_pypi(
    mock_find_in_dir,
    mock_aur,
    mock_repo,
    mock_pypi_meta,
    mock_pypi_deps,
    mock_pypi_verify,
):
    mock_find_in_dir.return_value = None
    mock_repo.return_value = None
    mock_aur.return_value = None

    mock_pypi_verify.side_effect = lambda x: x == "fastmcp"
    mock_pypi_deps.side_effect = lambda x: ["python-click"] if x == "fastmcp" else []
    mock_pypi_meta.return_value = {"version": "1.0.0"}

    # We need click to be resolved too
    def mock_repo_side_effect(pkg):
        return pkg if pkg == "python-click" else None

    mock_repo.side_effect = mock_repo_side_effect

    resolver = DependencyResolver(work_dir="work")
    resolver.resolve("python-fastmcp")

    assert "python-fastmcp" in resolver.graph.nodes
    assert resolver.graph.nodes["python-fastmcp"]["tier"] == "pypi"
    assert "python-click" in resolver.graph.nodes
    assert resolver.graph.nodes["python-click"]["tier"] == "repo"
    assert ("python-fastmcp", "python-click") in resolver.graph.edges


@patch("aur_python_packer.clients.PyPIClient.verify_existence")
@patch("aur_python_packer.resolver.DependencyResolver.pypi_get_dependencies")
@patch("aur_python_packer.clients.PyPIClient.get_metadata")
@patch("aur_python_packer.resolver.find_provider_in_repos")
@patch("aur_python_packer.clients.AURClient.get_info")
@patch("aur_python_packer.resolver.DependencyResolver._find_in_dir")
def test_resolve_pypi_redirect(
    mock_find_in_dir,
    mock_aur,
    mock_repo,
    mock_pypi_meta,
    mock_pypi_deps,
    mock_pypi_verify,
):
    mock_find_in_dir.return_value = None
    mock_repo.return_value = None
    mock_aur.return_value = None

    mock_pypi_verify.side_effect = lambda x: x == "fastmcp"
    mock_pypi_deps.return_value = []
    mock_pypi_meta.return_value = {"version": "1.0.0"}

    resolver = DependencyResolver(work_dir="work")
    resolver.resolve("fastmcp")

    assert "fastmcp" in resolver.graph.nodes
    assert "python-fastmcp" in resolver.graph.nodes
    assert resolver.graph.nodes["python-fastmcp"]["tier"] == "pypi"
    assert ("fastmcp", "python-fastmcp") in resolver.graph.edges


@patch("aur_python_packer.resolver.find_provider_in_repos")
@patch("aur_python_packer.clients.AURClient.get_info")
@patch("aur_python_packer.resolver.DependencyResolver._find_in_dir")
def test_resolve_provides(mock_find_in_dir, mock_aur, mock_repo_provider):
    mock_find_in_dir.return_value = None
    mock_aur.return_value = None

    # python-pyyaml is provided by python-yaml
    mock_repo_provider.side_effect = (
        lambda x: "python-yaml"
        if x == "python-pyyaml"
        else (x if x == "python-yaml" else None)
    )

    resolver = DependencyResolver(work_dir="work")
    resolver.resolve("python-pyyaml")

    assert "python-yaml" in resolver.graph.nodes
    assert resolver.graph.nodes["python-yaml"]["tier"] == "repo"
    assert ("python-pyyaml", "python-yaml") in resolver.graph.edges


@patch("aur_python_packer.resolver.find_provider_in_repos")
@patch("aur_python_packer.clients.AURClient.get_info")
@patch("aur_python_packer.resolver.DependencyResolver._find_in_dir")
def test_search_priority(mock_find_in_dir, mock_aur, mock_repo_provider):
    # 1. Hit in Newly Created (Tier 1)
    mock_find_in_dir.side_effect = (
        lambda pkg, dir: {"path": "packages/pkg", "depends": []}
        if "packages" in dir
        else None
    )
    resolver = DependencyResolver(work_dir="work")
    resolver.resolve("pkg")
    assert resolver.graph.nodes["pkg"]["tier"] == "local"

    # 2. Hit in Repo (Tier 2, not in Tier 1)
    mock_find_in_dir.side_effect = lambda pkg, dir: None
    mock_repo_provider.side_effect = lambda x: x
    resolver = DependencyResolver(work_dir="work")
    resolver.resolve("pkg2")
    assert resolver.graph.nodes["pkg2"]["tier"] == "repo"


@patch("aur_python_packer.resolver.find_provider_in_repos")
@patch("aur_python_packer.clients.AURClient.get_info")
@patch("aur_python_packer.resolver.DependencyResolver._find_in_dir")
def test_inject_dependency(mock_find_in_dir, mock_aur, mock_repo_provider):
    """inject_dependency resolves and adds an edge from target_pkg -> dep_name."""
    mock_find_in_dir.return_value = None
    mock_aur.return_value = None
    mock_repo_provider.side_effect = lambda x: x if x == "python-bar" else None

    resolver = DependencyResolver(work_dir="work")
    # Pre-add the target
    resolver.graph.add_node("pkg-a", tier="local", path=".", version="1.0")
    resolver.visited.add("pkg-a")

    resolver.inject_dependency("pkg-a", "python-bar")

    assert "python-bar" in resolver.graph.nodes
    assert resolver.graph.nodes["python-bar"]["tier"] == "repo"
    assert ("pkg-a", "python-bar") in resolver.graph.edges


@patch("aur_python_packer.resolver.find_provider_in_repos")
@patch("aur_python_packer.clients.AURClient.get_info")
@patch("aur_python_packer.resolver.DependencyResolver._find_in_dir")
def test_inject_dependency_multiple(mock_find_in_dir, mock_aur, mock_repo_provider):
    """Multiple injected dependencies all get resolved and added."""
    mock_find_in_dir.return_value = None
    mock_aur.return_value = None

    def repo_side(pkg):
        if pkg == "repo-pkg":
            return "repo-pkg"
        if pkg == "another-pkg":
            return "another-pkg"
        return None

    mock_repo_provider.side_effect = repo_side

    resolver = DependencyResolver(work_dir="work")
    resolver.graph.add_node("pkg-a", tier="local", path=".", version="1.0")
    resolver.visited.add("pkg-a")

    resolver.inject_dependency("pkg-a", "repo-pkg")
    resolver.inject_dependency("pkg-a", "another-pkg")

    assert ("pkg-a", "repo-pkg") in resolver.graph.edges
    assert ("pkg-a", "another-pkg") in resolver.graph.edges
