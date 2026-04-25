## ADDED Requirements

### Requirement: Dependency Metadata Extraction
The scanner SHALL extract `depends`, `makedepends`, and `checkdepends` from `PKGBUILD` files.

#### Scenario: Parse basic dependencies
- **WHEN** a `PKGBUILD` contains `depends=('python' 'python-pip')`
- **THEN** the scanner returns a list `['python', 'python-pip']` for the `depends` key

#### Scenario: Handle empty dependencies
- **WHEN** a `PKGBUILD` does not define `depends` or has an empty list
- **THEN** the scanner returns an empty list for that metadata field

### Requirement: Package Version and Name Extraction
The scanner SHALL extract the `pkgname` and `pkgver` from `PKGBUILD` files.

#### Scenario: Parse name and version
- **WHEN** a `PKGBUILD` contains `pkgname=python-jupyter-ai` and `pkgver=1.0.0`
- **THEN** the scanner returns `python-jupyter-ai` and `1.0.0` for the respective fields

### Requirement: Bash Variable Expansion Support
The scanner SHALL handle simple bash variable expansion for dependency names (e.g., `${_pkgname}`).

#### Scenario: Expand variables in dependencies
- **WHEN** a `PKGBUILD` defines `_pyname=jupyter-ai` and `depends=("python-${_pyname}")`
- **THEN** the scanner returns `['python-jupyter-ai']` as the dependency
