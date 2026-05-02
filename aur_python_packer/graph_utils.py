import re
import click
import networkx as nx
import dagviz

def print_dependency_graph(graph: nx.DiGraph, state_manager, show_repo_deps=False):
    """
    Prints the dependency graph with status annotations and colors.
    
    Nodes are annotated with [built] if they are already successfully built,
    or [failed] if a previous build attempt failed.
    Tiers are shown in brackets, e.g., (pypi).
    
    Args:
        graph: networkx.DiGraph representing the dependency tree.
        state_manager: StateManager instance to check package status.
        show_repo_deps: If False, omit 'repo' tier nodes if total nodes > 20.
    """
    # Filtering logic
    display_graph = graph
    omitted_count = 0
    if not show_repo_deps and len(graph.nodes) > 20:
        repo_nodes = [n for n, d in graph.nodes(data=True) if d.get("tier") == "repo"]
        omitted_count = len(repo_nodes)
        if omitted_count > 0:
            display_graph = graph.subgraph([n for n in graph.nodes if n not in repo_nodes])

    # Create a mapping for labels
    labels = {}
    for node, data in display_graph.nodes(data=True):
        tier = data.get("tier", "")
        pkg_state = state_manager.get_package(node)
        
        label = node
        if tier:
            label += f" ({tier})"
            
        if pkg_state and pkg_state.get("status") == "success":
            if pkg_state.get("skipped_checks"):
                label += " [built (no checks)]"
            else:
                label += " [built]"
        elif pkg_state and pkg_state.get("status") == "failed":
            label += " [failed]"
            
        labels[node] = label
    
    # Create a temporary graph with relabeled nodes for visualization
    relabeled_graph = nx.relabel_nodes(display_graph, labels)
    
    # Render to string using dagviz
    try:
        # py-dagviz.visualize_dag returns the ASCII/Unicode representation
        graph_str = dagviz.visualize_dag(relabeled_graph)
    except Exception as e:
        click.secho(f"Warning: Could not render dependency graph: {e}", fg="yellow", err=True)
        return

    # Post-processing for colorization to avoid dagviz layout issues with ANSI codes
    # 1a. Colorize [built] in green
    graph_str = re.sub(
        r"(\[built(?: \(no checks\))?\])", 
        lambda m: click.style(m.group(1), fg="green", bold=True), 
        graph_str
    )
    
    # 1b. Colorize [failed] in red
    graph_str = re.sub(
        r"\[failed\]", 
        click.style("[failed]", fg="red", bold=True), 
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

    if omitted_count > 0:
        click.echo(
            f"Note: Omitted {omitted_count} repository dependencies from visualization. Use --show-repo-deps to see full graph."
        )
