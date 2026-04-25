import click
from aur_lifecycle_mgr.main import Manager
from aur_lifecycle_mgr.audit import Auditor

@click.group()
@click.option('--state', default="build_state.json", help="Path to state file")
@click.option('--repo', default="local_repo", help="Path to local repository")
@click.pass_context
def main(ctx, state, repo):
    """AUR Lifecycle Manager - Automate AUR package builds."""
    ctx.obj = Manager(state_file=state, repo_dir=repo)

@main.command()
@click.argument('pkgname')
@click.pass_obj
def build(mgr, pkgname):
    """Build a package and its dependencies."""
    mgr.build_all(pkgname)

@main.command()
@click.pass_obj
def audit(mgr):
    """Check for outdated packages against PyPI."""
    auditor = Auditor(mgr.state.state)
    report = auditor.audit()
    if not report:
        click.echo("No packages found in state to audit.")
        return

    for pkg, info in report.items():
        status = "OUTDATED" if info['outdated'] else "UP-TO-DATE"
        click.echo(f"{pkg}: {info['current']} -> {info['latest']} [{status}]")

if __name__ == "__main__":
    main()
