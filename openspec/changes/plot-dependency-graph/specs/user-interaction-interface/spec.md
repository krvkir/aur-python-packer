## ADDED Requirements

### Requirement: Dependency Graph Visualization
The system SHALL provide a graphical representation of the dependency DAG (Directed Acyclic Graph) to allow users to visualize complex relationships and build status during the resolution process.

#### Scenario: Visualizing dependency DAG
- **GIVEN** a package with dependencies
- **WHEN** the user resolves dependencies
- **THEN** the system SHALL output an ASCII/Unicode DAG visualization
- **AND** it SHALL highlight nodes that are already successfully built
- **AND** it SHALL support ANSI colors in interactive terminals while ensuring they are stripped for non-TTY output
