## 1. Template and Metadata Logic Updates

- [ ] 1.1 Update `aur_python_packer/templates/PKGBUILD.j2` with stable source URLs and license installation
- [ ] 1.2 Improve license normalization in `aur_python_packer/generator.py` to use SPDX identifiers
- [ ] 1.3 Update `PyPIGenerator.generate` to use the stable PyPI URL scheme

## 2. Maintainer Support Implementation

- [ ] 2.1 Extract git identity discovery into a utility function in `aur_python_packer/utils.py`
- [ ] 2.2 Update `PyPIGenerator` to accept a `maintainer` attribute and use it in the template
- [ ] 2.3 Update `Manager` to use the new utility as a default for maintainer info
- [ ] 2.4 Add `--maintainer` option to the CLI to allow manual overrides

## 3. Robustness and Compliance Fixes

- [ ] 3.1 Update PKGBUILD directory handling to use specific `${_name}-${pkgver}`
- [ ] 3.2 Add fallback for missing `url` metadata in `generator.py`
- [ ] 3.3 Ensure VCS packages do not use improper `replaces` field

## 4. Verification and Regeneration

- [ ] 4.1 Regenerate PKGBUILDs in the test workspace
- [ ] 4.2 Verify compliance using `namcap` on generated files
- [ ] 4.3 Perform a test build of a representative package (e.g., `python-jupyter-ai`) in a clean chroot
