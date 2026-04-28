import re
import click
import networkx as nx
import dagviz

def print_dependency_graph(graph: nx.DiGraph, state_manager):
    """
    Prints the dependency graph with status annotations and colors.
    
    Nodes are annotated with [built] if they are already successfully built.
    Tiers are shown in brackets, e.g., (pypi).
    
    Args:
        graph: networkx.DiGraph representing the dependency tree.
        state_manager: StateManager instance to check package status.
    """
    # Create a mapping for labels
    labels = {}
    for node, data in graph.nodes(data=True):
        tier = data.get("tier", "")
        pkg_state = state_manager.get_package(node)
        
        label = node
        if tier:
            label += f" ({tier})"
            
        if pkg_state and pkg_state.get("status") == "success":
            label += " [built]"
            
        labels[node] = label
    
    # Create a temporary graph with relabeled nodes for visualization
    relabeled_graph = nx.relabel_nodes(graph, labels)
    
    # Render to string using dagviz
    try:
        # py-dagviz.visualize_dag returns the ASCII/Unicode representation
        graph_str = dagviz.visualize_dag(relabeled_graph)
    except Exception as e:
        click.secho(f"Warning: Could not render dependency graph: {e}", fg="yellow", err=True)
        return

    # Post-processing for colorization to avoid dagviz layout issues with ANSI codes
    # 1. Colorize [built] in green
    graph_str = re.sub(
        r"\[built\]", 
        click.style("[built]", fg="green", bold=True), 
        graph_str
    )
    
    # 2. Colorize tiers in cyan
    graph_str = re.sub(
        r"\((repo|local|aur|pypi)\)", 
        lambda m: click.style(m.group(0), fg="cyan"), 
        graph_str
    )
    
    # 3. Colorize package names
    def colorize_pkg(match):
        tree_prefix = match.group(1)
        pkg_name = match.group(2)
        return tree_prefix + click.style(pkg_name, fg="white", bold=True)

    # regex to match tree prefix (non-newlines followed by a bullet and space) and then the package name
    graph_str = re.sub(
        r"([^•\n]*•\s+)([a-zA-Z0-9\-_.]+)", 
        colorize_pkg, 
        graph_str
    )

    click.echo("\nDependency Graph:")
    click.echo(graph_str)
