## MODIFIED Requirements

### Requirement: Packaging Artifact Generation
The system SHALL generate a valid `PKGBUILD` file using a standardized Jinja2 template and subsequently generate `.SRCINFO` using native Arch Linux tools. The generated PKGBUILD MUST comply with Arch Linux Python package and AUR submission guidelines, including stable source URLs and automated license installation.

#### Scenario: Generate for new package
- **GIVEN** metadata has been retrieved for a package
- **WHEN** generating artifacts
- **THEN** the system SHALL render a `PKGBUILD` from a template using a stable PyPI source URL (`https://files.pythonhosted.org/packages/source/...`)
- **AND** it SHALL include a `package()` function that installs the `LICENSE` file to `/usr/share/licenses/$pkgname/`
- **AND** it SHALL execute `makepkg --printsrcinfo` to generate the corresponding `.SRCINFO` file

## ADDED Requirements

### Requirement: Maintainer Attribution
The system SHALL support the inclusion of maintainer information at the top of generated PKGBUILD files to comply with AUR submission requirements.

#### Scenario: Successful maintainer attribution
- **GIVEN** a maintainer identity is configured (e.g., "John Doe <john@example.com>")
- **WHEN** the system generates a PKGBUILD
- **THEN** it SHALL prepend a `# Maintainer: John Doe <john@example.com>` comment to the file
