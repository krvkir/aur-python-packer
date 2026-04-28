import json
import os

import click

from aur_python_packer.graph_utils import print_dependency_graph
from aur_python_packer.logger import setup_logging
from aur_python_packer.main import Manager


@click.group()
@click.option(
    "--work-dir",
    "-w",
    default="work",
    type=click.Path(file_okay=False),
    help="Base directory for all tool state and artifacts.",
)
@click.pass_context
def cli(ctx, work_dir):
    """AUR Python Packer - Automate AUR package builds."""
    ctx.ensure_object(dict)
    ctx.obj["work_dir"] = work_dir


@cli.command()
@click.argument("pkgname")
@click.option("--path", "-P", multiple=True, help="Search paths for local PKGBUILDs")
@click.option("--nocheck", is_flag=True, help="Skip package checks (tests)")
@click.pass_context
def build(ctx, pkgname, path, nocheck):
    """Build a package and its dependencies."""
    workdir = ctx.obj["work_dir"]
    log_path = setup_logging(workdir)
    print(f"Logging to: {log_path}")

    mgr = Manager(work_dir=workdir)
    if path:
        mgr.resolver.search_paths = list(path)

    try:
        mgr.build_all(pkgname, nocheck=nocheck)
    except ValueError as e:
        click.secho(str(e), fg="red", err=True)
        ctx.exit(1)


@cli.command()
@click.argument("pkgname")
@click.option("--path", "-P", multiple=True, help="Search paths for local PKGBUILDs")
@click.pass_context
def resolve(ctx, pkgname, path):
    """Resolve dependencies for a package and print details."""
    workdir = ctx.obj["work_dir"]
    setup_logging(workdir)

    mgr = Manager(work_dir=workdir)
    if path:
        mgr.resolver.search_paths = list(path)

    print(f"Resolving dependencies for {pkgname}...")
    try:
        mgr.resolver.resolve(pkgname)
    except ValueError as e:
        click.secho(str(e), fg="red", err=True)
        ctx.exit(1)

    print_dependency_graph(mgr.resolver.graph, mgr.state)

    order = mgr.resolver.get_build_order()

    print(f"\nBuild Order / Resolved Packages:")
    for pkg in order:
        node = mgr.resolver.graph.nodes[pkg]
        tier = node.get("tier", "unknown")
        version = node.get("version", "N/A")
        deps = list(mgr.resolver.graph.successors(pkg))

        print(f"\nPackage: {pkg}")
        print(f"  Tier:    {tier}")
        print(f"  Version: {version}")
        if deps:
            print(f"  Depends: {', '.join(deps)}")
        else:
            print(f"  Depends: (none)")

        # Print extra metadata if available
        extra = {k: v for k, v in node.items() if k not in ["tier", "version"]}
        if extra:
            print(f"  Metadata: {json.dumps(extra)}")


@cli.command()
@click.argument("command")
@click.option("--cwd", help="Working directory inside the sandbox")
@click.pass_context
def cmd(ctx, command, cwd):
    """Execute a command inside the chrooted environment."""
    workdir = ctx.obj["work_dir"]
    log_path = setup_logging(workdir)
    print(f"Logging to: {log_path}")

    mgr = Manager(work_dir=workdir)
    mgr.run_in_sandbox(command, cwd=cwd or workdir, check=False)


def main():
    cli()


if __name__ == "__main__":
    main()
