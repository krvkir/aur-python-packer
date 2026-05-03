## Why

Currently generated PKGBUILDs violate multiple Arch Linux and AUR submission guidelines, including the use of non-stable hashed PyPI URLs, missing maintainer headers, and failure to install license files. These issues prevent the generated packages from being accepted into the AUR and reduce their overall quality and reliability.

## What Changes

- **Template Update**: Modify `PKGBUILD.j2` to use the stable PyPI source URL scheme and robust directory handling (`${_name}-${pkgver}`).
- **License Installation**: Add automated `LICENSE` file installation to the `package()` function in the PKGBUILD template.
- **Maintainer Support**: Introduce a mechanism to include `# Maintainer` information at the top of generated PKGBUILDs.
- **License Normalization**: Enhance the generator's license mapping to prioritize SPDX identifiers (e.g., `Apache-2.0`).
- **Metadata Robustness**: Ensure `url` fields are always populated (falling back to PyPI project pages) and remove improper `replaces` fields in VCS packages.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `package-generation`: Update PKGBUILD generation requirements to include AUR compliance (stable URLs, maintainer headers, license installation).

## Impact

- `aur_python_packer/generator.py`: Updated logic for metadata processing and template rendering.
- `aur_python_packer/templates/PKGBUILD.j2`: Updated template structure and logic.
- Generated packages in `packages/` directory will require regeneration to become compliant.
