import pytest
from unittest.mock import patch, MagicMock
from aur_python_packer.resolver import DependencyResolver

def test_topological_sort_linear():
    resolver = DependencyResolver()
    resolver.graph.add_edge("A", "B") # A depends on B
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

@patch('aur_python_packer.resolver.is_in_repos')
@patch('aur_python_packer.resolver.get_aur_info')
@patch('os.path.isdir')
def test_resolve_cascade(mock_isdir, mock_aur, mock_repo):
    # Setup mocks
    mock_isdir.return_value = False # No local
    mock_repo.side_effect = lambda x: x == "pacman" # pacman is in repo
    mock_aur.side_effect = lambda x: {"Depends": ["pacman"]} if x == "aur-pkg" else None
    
    resolver = DependencyResolver()
    resolver.resolve("aur-pkg")
    
    assert "aur-pkg" in resolver.graph.nodes
    assert "pacman" in resolver.graph.nodes
    assert ("aur-pkg", "pacman") in resolver.graph.edges
    assert resolver.get_build_order() == ["pacman", "aur-pkg"]

@patch('aur_python_packer.resolver.pypi_verify_existence')
@patch('aur_python_packer.resolver.DependencyResolver.pypi_get_dependencies')
@patch('aur_python_packer.resolver.pypi_get_full_meta')
@patch('aur_python_packer.resolver.is_in_repos')
@patch('aur_python_packer.resolver.get_aur_info')
@patch('os.path.isdir')
def test_resolve_pypi(mock_isdir, mock_aur, mock_repo, mock_pypi_meta, mock_pypi_deps, mock_pypi_verify):
    mock_isdir.return_value = False
    mock_repo.return_value = False
    mock_aur.return_value = None
    
    mock_pypi_verify.side_effect = lambda x: x == "fastmcp"
    mock_pypi_deps.side_effect = lambda x: ["python-click"] if x == "fastmcp" else []
    mock_pypi_meta.return_value = {"version": "1.0.0"}
    
    # We need click to be resolved too
    def mock_repo_side_effect(pkg):
        return pkg == "python-click"
        
    mock_repo.side_effect = mock_repo_side_effect
    
    resolver = DependencyResolver()
    resolver.resolve("python-fastmcp")
    
    assert "python-fastmcp" in resolver.graph.nodes
    assert resolver.graph.nodes["python-fastmcp"]["tier"] == "pypi"
    assert "python-click" in resolver.graph.nodes
    assert resolver.graph.nodes["python-click"]["tier"] == "repo"
    assert ("python-fastmcp", "python-click") in resolver.graph.edges

@patch('aur_python_packer.resolver.pypi_verify_existence')
@patch('aur_python_packer.resolver.DependencyResolver.pypi_get_dependencies')
@patch('aur_python_packer.resolver.pypi_get_full_meta')
@patch('aur_python_packer.resolver.is_in_repos')
@patch('aur_python_packer.resolver.get_aur_info')
@patch('os.path.isdir')
def test_resolve_pypi_redirect(mock_isdir, mock_aur, mock_repo, mock_pypi_meta, mock_pypi_deps, mock_pypi_verify):
    mock_isdir.return_value = False
    mock_repo.return_value = False
    mock_aur.return_value = None
    
    mock_pypi_verify.side_effect = lambda x: x == "fastmcp"
    mock_pypi_deps.return_value = []
    mock_pypi_meta.return_value = {"version": "1.0.0"}
    
    resolver = DependencyResolver()
    resolver.resolve("fastmcp")
    
    assert "fastmcp" in resolver.graph.nodes
    assert "python-fastmcp" in resolver.graph.nodes
    assert resolver.graph.nodes["python-fastmcp"]["tier"] == "pypi"
    assert ("fastmcp", "python-fastmcp") in resolver.graph.edges
