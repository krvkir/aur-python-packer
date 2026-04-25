import os
from aur_lifecycle_mgr.resolver import DependencyResolver
from aur_lifecycle_mgr.builder import BuildOrchestrator
from aur_lifecycle_mgr.repo import RepoManager
from aur_lifecycle_mgr.state import StateManager
from aur_lifecycle_mgr.generator import PyPIGenerator, generate_srcinfo

class Manager:
    def __init__(self, state_file="build_state.json", repo_dir="local_repo"):
        self.state = StateManager(state_file)
        self.repo = RepoManager(repo_dir)
        self.builder = BuildOrchestrator()
        self.resolver = DependencyResolver()
        self.generator = PyPIGenerator()

    def build_all(self, target_pkg):
        print(f"Resolving dependencies for {target_pkg}...")
        self.resolver.resolve(target_pkg)
        order = self.resolver.get_build_order()
        print(f"Build order: {' -> '.join(order)}")

        for pkg in order:
            node_data = self.resolver.graph.nodes[pkg]
            tier = node_data.get('tier')
            
            # Check if already built in this run or previous
            current_state = self.state.get_package(pkg)
            if current_state and current_state['status'] == 'success':
                print(f"Package {pkg} already built, skipping.")
                continue

            print(f"Processing {pkg} (Tier: {tier})...")
            
            if tier == 'repo':
                print(f"{pkg} is in official repos, no build needed.")
                continue

            pkg_dir = None
            if tier == 'local':
                pkg_dir = node_data['path']
            elif tier == 'aur':
                # TODO: Implement AUR git clone
                print(f"AUR clone not yet implemented for {pkg}")
                continue
            elif tier == 'pypi':
                pyname = pkg.replace('python-', '')
                pkg_dir = os.path.join("generated", pkg)
                self.generator.generate(pyname, pkg_dir)
                generate_srcinfo(pkg_dir)
            
            if pkg_dir:
                try:
                    pkg_file = self.builder.build(pkg, pkg_dir)
                    self.repo.add_package(pkg_file)
                    # We need a version here. For local/pypi we can parse it.
                    # Simplified for now.
                    self.state.update_package(pkg, "built", "success")
                    print(f"Successfully built and added {pkg}")
                except Exception as e:
                    print(f"Failed to build {pkg}: {e}")
                    self.state.update_package(pkg, "failed", "error")
                    break
