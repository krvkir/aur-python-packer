## Context

The `aur-python-packer` tool currently generates PKGBUILDs that fail basic AUR submission checks. The most critical failures are the use of volatile hashed PyPI URLs, the absence of maintainer information, and the lack of automated license file installation. 

## Goals / Non-Goals

**Goals:**
- Transition to stable, predictable PyPI source URLs.
- Ensure all generated PKGBUILDs include a valid `# Maintainer` header.
- Automate the installation of license files to the correct system directory.
- Improve license normalization to use standard SPDX identifiers.
- Refine directory handling in the build process for better robustness.

**Non-Goals:**
- Implementing a full PyPI-to-SPDX mapping database (using heuristics for now).
- Handling complex multi-license scenarios or complex build-time dependencies beyond basic PEP 517.

## Decisions

### 1. Use Stable PyPI Source URLs
**Decision**: Switch from hashed URLs to the `https://files.pythonhosted.org/packages/source/${_name::1}/${_name}/${_name}-$pkgver.tar.gz` format.
**Rationale**: This is the recommended stable scheme in the Arch Linux Python package guidelines, ensuring that PKGBUILDs remain valid even if PyPI caches change.
**Alternatives**: Using the hash-based URLs (current state), which are brittle and discouraged.

### 2. Standardized License Installation
**Decision**: Inject `install -Dm644 LICENSE -t "$pkgdir/usr/share/licenses/$pkgname/"` into the `package()` function.
**Rationale**: Required by Arch Linux guidelines for most non-GPL licenses to ensure transparency. 
**Implementation**: The template will assume a file named `LICENSE` exists in the source root. Future improvements could dynamically detect the license filename.

### 3. Maintainer Information Injection
**Decision**: Automatically discover maintainer identity from `git config --global user.name` and `user.email`. Allow override via CLI/config.
**Rationale**: Mandatory for AUR submission. Reusing existing system configuration minimizes user friction and ensures consistency with local git commits.
**Alternatives**: Requiring explicit configuration for every run.

### 4. Robust Directory Handling
**Decision**: Use `cd "${_name}-${pkgver}"` instead of `cd "$srcdir"/*-"$pkgver"`.
**Rationale**: Less prone to errors if multiple directories matching the pattern exist in srcdir.

## Risks / Trade-offs

- **[Risk] Missing License File** → [Mitigation] If the upstream package does not include a file literally named `LICENSE`, the build might fail. We will stick to the common standard for now and consider adding a check or fallback later.
- **[Risk] Incorrect License Normalization** → [Mitigation] The heuristic in `generator.py` will be improved but will still fall back to the original string or "custom" to avoid breaking the build.
