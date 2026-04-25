## 1. Project Setup

- [ ] 1.1 Create the scanner script/module structure in `scripts/aur_scanner.py`.
- [ ] 1.2 Define the data structure for package metadata (TypedDict or dataclass).

## 2. Directory Discovery

- [ ] 2.1 Implement recursive file search to locate all `PKGBUILD` files.
- [ ] 2.2 Filter out directories that should be ignored (e.g., `.git`, `build`, `src`).

## 3. Metadata Extraction

- [ ] 3.1 Implement a helper function to source a `PKGBUILD` and extract variables (`pkgname`, `pkgver`, `depends`, `makedepends`, `checkdepends`) as JSON.
- [ ] 3.2 Implement logic to parse the JSON output back into Python objects.
- [ ] 3.3 Add handling for optional/missing metadata fields.

## 4. Aggregation and Validation

- [ ] 4.1 Create a central registry mapping `pkgname` to its metadata.
- [ ] 4.2 Implement detection for duplicate `pkgname` definitions across different paths.
- [ ] 4.3 Add a CLI interface to trigger the scan and output the result (e.g., `--root` and `--output`).

## 5. Verification

- [ ] 5.1 Create a test suite with sample `PKGBUILD` files (including variables and multi-line lists).
- [ ] 5.2 Verify that all dependencies are correctly extracted and variables expanded.
