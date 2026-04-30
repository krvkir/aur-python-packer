# Design: Smart Resolver

## Component Changes

### 1. `DependencyResolver` (`aur_python_packer/resolver.py`)
- Update the `resolve` method to implement the 4-tier sequence.
- Integrate "Provides" check into the repo search logic.
- Call `aur_client.clone_repo` immediately when a package is found in AUR RPC and is not already in `aur_packages/`.

### 2. Repo Search ("Provides" Support)
- Use `pacman -Sp --print-format %n <pkgname>` or similar to check for providers.
- Alternatively, use `pacman -Si <pkgname>` and parse the output, but `pacman -Ssq ^pkgname$` might be better for names, and `pacman -Ssq --provides pkgname` for provides.
- Actually, `pacman -Si <pkgname>` is fast for direct hits. For provides, we can use `pacman -Ssq --provides pkgname` or parse the local sync database if necessary. 
- A simple approach: `run_command(["pacman", "-Si", pkgname])`. If it fails, try `run_command(["pacman", "-Ssq", f"^{pkgname}$"])`. If that fails, `run_command(["pacman", "-Ssq", "--provides", pkgname])`.

### 3. Early AUR Cloning
- When `DependencyResolver` identifies a package in the AUR, it must ensure it's cloned to `aur_packages/` before proceeding to resolve its dependencies. This allows the resolver to then parse the *local* PKGBUILD/SRCINFO for dependencies instead of relying solely on the AUR RPC metadata (which might be slightly different or less complete for complex builds).

### 4. Integration with `Manager`
- `Manager` will no longer be responsible for cloning AUR repos during the build loop. It will assume all necessary sources are already in `packages/` or `aur_packages/`.
