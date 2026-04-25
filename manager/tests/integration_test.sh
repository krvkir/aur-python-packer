#!/bin/bash
set -e

# Setup a clean test environment
TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

echo "Using temp dir: $TEST_DIR"

# Create a dummy local package
mkdir -p "$TEST_DIR/local_packages/python-dummy"
cat > "$TEST_DIR/local_packages/python-dummy/PKGBUILD" <<EOF
pkgname=python-dummy
pkgver=1.0.0
pkgrel=1
pkgdesc="A dummy package for testing"
arch=('any')
url="http://example.com"
license=('MIT')
depends=('python')
source=()
package() {
    mkdir -p "\$pkgdir/usr/share/dummy"
    touch "\$pkgdir/usr/share/dummy/test"
}
EOF

# Run the manager
PYTHONPATH=src venv/bin/python src/aur_lifecycle_mgr/cli.py \
    --state "$TEST_DIR/state.json" \
    --repo "$TEST_DIR/repo" \
    --path "$TEST_DIR/local_packages" \
    build python-dummy

# Verify results
if [ ! -f "$TEST_DIR/repo/python-dummy-1.0.0-1-any.pkg.tar.zst" ]; then
    echo "FAILED: Package not found in repo"
    exit 1
fi

if [ ! -f "$TEST_DIR/repo/localrepo.db.tar.gz" ]; then
    echo "FAILED: Repo database not found"
    exit 1
fi

# Check state.json
grep -q "success" "$TEST_DIR/state.json" || (echo "FAILED: State not updated to success"; exit 1)

echo "INTEGRATION TEST PASSED"
