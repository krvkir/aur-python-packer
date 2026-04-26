## ADDED Requirements

### Requirement: Local Repository Maintenance
The system SHALL maintain a local pacman repository directory containing all successfully built packages.

#### Scenario: Add package to repo
- **WHEN** a package is built successfully
- **THEN** the system SHALL move it to the repository directory and run `repo-add` to update the database.

### Requirement: Chroot Configuration Injection
The system SHALL modify the chroot's configuration to include the local repository as a trusted source.

#### Scenario: Configure pacman.conf
- **WHEN** preparing a chroot for a build
- **THEN** the system SHALL append the local repository path to the chroot's `/etc/pacman.conf` with `SigLevel = Optional TrustAll`.
