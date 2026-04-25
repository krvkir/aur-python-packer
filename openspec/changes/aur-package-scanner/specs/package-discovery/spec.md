## ADDED Requirements

### Requirement: Recursive PKGBUILD Discovery
The scanner SHALL recursively traverse a specified directory to find all files named `PKGBUILD`.

#### Scenario: Discover single PKGBUILD
- **WHEN** the scanner is pointed at a directory containing one `PKGBUILD`
- **THEN** the scanner returns the path to that `PKGBUILD`

#### Scenario: Discover multiple PKGBUILDs in subdirectories
- **WHEN** the scanner is pointed at a directory with multiple subdirectories, each containing a `PKGBUILD`
- **THEN** the scanner returns a list of paths to all discovered `PKGBUILD` files

### Requirement: Duplicate Package Detection
The scanner SHALL identify and report if the same `pkgname` is found in multiple locations within the scanned directory.

#### Scenario: Report duplicate packages
- **WHEN** two `PKGBUILD` files define the same `pkgname`
- **THEN** the scanner records both paths and flags the duplication for the user
