## 1. Environment & Dependencies

- [ ] 1.1 Add `packaging` to `pyproject.toml` dependencies.
- [ ] 1.2 Run `poetry lock` or equivalent to update the environment.

## 2. Core Implementation: PyPI Verification

- [ ] 2.1 Implement a standalone `pypi_verify_existence(pyname)` function in `generator.py` or `resolver.py`.
- [ ] 2.2 Update `DependencyResolver.resolve` to use `pypi_verify_existence` instead of the `python-` prefix check.
- [ ] 2.3 Update the mapping logic in `DependencyResolver` to handle `python-` prefixed names by stripping the prefix for PyPI lookups.

## 3. Core Implementation: Dependency Extraction

- [ ] 3.1 Update `PyPIGenerator.fetch_meta` to extract the `requires_dist` field from the PyPI JSON response.
- [ ] 3.2 Implement a utility function to parse PEP 508 strings using `packaging.requirements`.
- [ ] 3.3 Implement a name normalization utility to map PyPI project names to Arch `python-` package names.
- [ ] 3.4 Integrate parsed dependencies into the `DependencyResolver` flow to allow recursive resolution.

## 4. PKGBUILD Generation Updates

- [ ] 4.1 Update the `PKGBUILD` template in `generator.py` to ensure it correctly renders the `depends` array with mapped Arch names.
- [ ] 4.2 Update `PyPIGenerator.generate` to pass the resolved dependency list to the template.

## 5. Verification & Testing

- [ ] 5.1 Update existing unit tests in `tests/test_generator.py` to reflect the new metadata structure and API calls.
- [ ] 5.2 Add a new integration test case for a package known to have PyPI dependencies (e.g., `fastmcp` or `requests`).
- [ ] 5.3 Manually verify that directory naming and `PKGBUILD` paths follow the `python-<name>` convention.
