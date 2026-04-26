import click
from aur_python_packer.main import Manager

@click.command()
@click.argument('workdir', type=click.Path(file_okay=False))
@click.argument('pkgname')
@click.option('--local', is_flag=True, help="Build on local host instead of chroot")
@click.option('--path', '-P', multiple=True, help="Search paths for local PKGBUILDs")
@click.option('--nocheck', is_flag=True, help="Skip package checks (tests)")
def main(workdir, pkgname, local, path, nocheck):
    """AUR Python Packer - Automate AUR package builds."""
    mgr = Manager(work_dir=workdir, local_only=local)
    if path:
        mgr.resolver.search_paths = list(path)
    
    mgr.build_all(pkgname, nocheck=nocheck)

if __name__ == "__main__":
    main()
