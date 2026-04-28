#!/bin/bash
set -e

# Setup a clean test environment
TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

echo "Using temp dir: $TEST_DIR"
mkdir -p "$TEST_DIR/bin"
export PATH="$TEST_DIR/bin:$PATH"

# Create shims to avoid real bubblewrap/pacman/makepkg execution
cat > "$TEST_DIR/bin/bwrap" <<'EOF'
#!/bin/bash
CHDIR="."
while [[ $# -gt 0 ]]; do
    case "$1" in
        --chdir)
            CHDIR="$2"
            shift 2
            ;;
        pacman|makepkg|updpkgsums|repo-add)
            cd "$CHDIR" && exec "$@"
            ;;
        *)
            shift
            ;;
    esac
done
EOF

cat > "$TEST_DIR/bin/pacman" <<'EOF'
#!/bin/bash
if [[ "$*" == *"-Sy"* ]]; then
    exit 0
fi
if [[ "$*" == *"-T"* ]]; then
    exit 0
fi
echo "Mock pacman called with: $*"
exit 0
EOF

cat > "$TEST_DIR/bin/makepkg" <<'EOF'
#!/bin/bash
if [[ "$*" == *"--printsrcinfo"* ]]; then
    echo "pkgname = python-dummy"
    echo "pkgver = 1.0.0"
    echo "pkgrel = 1"
    exit 0
fi
source PKGBUILD
touch "${pkgname}-${pkgver}-${pkgrel}-any.pkg.tar.zst"
EOF

cat > "$TEST_DIR/bin/updpkgsums" <<'EOF'
#!/bin/bash
exit 0
EOF

cat > "$TEST_DIR/bin/repo-add" <<'EOF'
#!/bin/bash
db_file="$1"
touch "$db_file"
# Create the .db symlink that pacman/repo-add usually creates
db_dir=$(dirname "$db_file")
db_base=$(basename "$db_file" .tar.gz)
ln -sf "$(basename "$db_file")" "$db_dir/${db_base%.db}"
EOF

chmod +x "$TEST_DIR/bin/"*

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

# Pre-create the fakeroot dummy in the work dir to skip bootstrapping
# The tool expects it at $WORK_DIR/root/usr/bin/fakeroot
WORK_DIR="$TEST_DIR/work"
mkdir -p "$WORK_DIR/root/usr/bin"
touch "$WORK_DIR/root/usr/bin/fakeroot"

# Run the manager using the new CLI
# aur-python-packer -w <workdir> build <pkgname> --path <search_path> --nocheck
poetry run aur-python-packer -w "$WORK_DIR" build python-dummy \
    --path "$TEST_DIR/local_packages" \
    --nocheck

# Verify results
if [ ! -f "$WORK_DIR/local_repo/python-dummy-1.0.0-1-any.pkg.tar.zst" ]; then
    echo "FAILED: Package not found in repo"
    ls -R "$WORK_DIR"
    exit 1
fi

if [ ! -f "$WORK_DIR/local_repo/localrepo.db.tar.gz" ]; then
    echo "FAILED: Repo database not found"
    exit 1
fi

# Check build_index.json
grep -q "success" "$WORK_DIR/build_index.json" || (echo "FAILED: State not updated to success"; exit 1)

echo "INTEGRATION TEST PASSED"
