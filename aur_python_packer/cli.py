import click
import json
from aur_python_packer.main import Manager
from aur_python_packer.logger import setup_logging

@click.group()
def cli():
    """AUR Python Packer - Automate AUR package builds."""
    pass

@cli.command()
@click.argument('workdir', type=click.Path(file_okay=False))
@click.argument('pkgname')
@click.option('--path', '-P', multiple=True, help="Search paths for local PKGBUILDs")
@click.option('--nocheck', is_flag=True, help="Skip package checks (tests)")
def build(workdir, pkgname, path, nocheck):
    """Build a package and its dependencies."""
    log_path = setup_logging(workdir)
    print(f"Logging to: {log_path}")

    mgr = Manager(work_dir=workdir)
    if path:
        mgr.resolver.search_paths = list(path)
    
    mgr.build_all(pkgname, nocheck=nocheck)

@cli.command()
@click.argument('workdir', type=click.Path(file_okay=False))
@click.argument('pkgname')
@click.option('--path', '-P', multiple=True, help="Search paths for local PKGBUILDs")
def resolve(workdir, pkgname, path):
    """Resolve dependencies for a package and print details."""
    setup_logging(workdir)
    
    mgr = Manager(work_dir=workdir)
    if path:
        mgr.resolver.search_paths = list(path)
    
    print(f"Resolving dependencies for {pkgname}...")
    mgr.resolver.resolve(pkgname)
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
        extra = {k: v for k, v in node.items() if k not in ['tier', 'version']}
        if extra:
            print(f"  Metadata: {json.dumps(extra)}")

def main():
    cli()

if __name__ == "__main__":
    main()
