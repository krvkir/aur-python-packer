#!/bin/bash
set -e

# Detect toolchain (Arch devtools vs Manjaro chrootbuild)
echo -e "\n\033[1;34m==> Initializing Build Environment...\033[0m"
if command -v extra-x86_64-build &> /dev/null; then
    BUILD_TOOL="arch"
    BUILD_CMD=("extra-x86_64-build")
    INJECT_FLAG="-I"
    echo " -> Detected Arch Linux toolchain (devtools)"
elif command -v chrootbuild &> /dev/null; then
    BUILD_TOOL="manjaro"
    BUILD_CMD=("sudo" "chrootbuild" "-c" "-p" ".")
    INJECT_FLAG="-i"
    echo " -> Detected Manjaro toolchain (manjaro-chrootbuild)"
else
    echo -e "\033[1;31mError: Missing clean chroot build tools.\033[0m"
    echo "On Arch Linux: sudo pacman -S devtools namcap"
    echo "On Manjaro: sudo pacman -S manjaro-chrootbuild namcap"
    exit 1
fi

if ! command -v namcap &> /dev/null; then
    echo -e "\033[1;31mError: 'namcap' is required for this test.\033[0m"
    echo "Please install it via: sudo pacman -S namcap"
    exit 1
fi

# ==============================================================================
# PACKAGE LISTS
# ==============================================================================

# External AUR dependencies (Fixes "target not found" pacman errors)
# Format: "package-name" OR "package-name:missing_dep1 missing_dep2"
# If a package spec is broken and missing dependencies, list them after a colon.
AUR_DEPENDENCIES=(
    "python-backoff"
    "python-opencensus"
    "python-tinycss2-1.4:python-flit-core"
    # "python-hatchling-git"
    # "python-rfc3987-syntax"

    # 'python-hatch-jupyter-builder'
    # 'python-hatch-nodejs-version'
    # # 'npm'
    # # 'jupyterlab'
    # 'python-terminado'
    # 'python-tinycss2'
    # 'python-rfc3986-validator'
    # 'python-rfc3987-syntax'
    # 'python-isoduration'
    # 'python-uri-template'
    # 'python-rfc3339-validator'
    # 'python-tzdata'
    # 'python-fqdn'
    # 'python-jsonpointer'
    # 'python-webcolors'
    # 'jupyter-lsp'

    # "python-opentelemetry-api"
    "python-fastmcp"
    "python-jsonref"
    # "python-langchain"

    # "python-opentelemetry"
    # Example of patching a broken AUR spec:
    # "python-broken-package:python-hatchling python-pytest"
)

# Topological order of local packages
PACKAGES=(
    "python-jupyterlab-eventlistener" # ok
    "python-jupyterlab-cell-input-footer" # ok
    "python-jupyter-server-mcp"
    "python-jupyterlab-chat"
    "python-jupyter-ai-litellm"
    "python-jupyterlab-notebook-awareness"
    "python-jupyter-ai-tools"
    "python-jupyterlab-diff"
    "python-jupyter-server-documents"
    "python-jupyter-ai-router"
    "python-jupyterlab-commands-toolkit"
    "python-jupyter-ai-persona-manager"
    "python-jupyter-ai-chat-commands"
    "python-jupyter-ai-jupyternaut"
    "python-jupyter-ai-magic-commands" # ok
    "python-jupyter-ai"
)

# ==============================================================================
# INJECTION SETUP
# ==============================================================================
CHROOT_INJECT_ARGS=()
FAILED_PACKAGES=()
SUCCESS_PACKAGES=()

echo -e "\n\033[1;34m==> Scanning for existing pre-built packages to inject...\033[0m"
shopt -s nullglob
for ext_pkg in *.pkg.tar.zst; do
    if [ -f "$ext_pkg" ]; then
        echo " -> Found external package $ext_pkg, adding to chroot inject list."
        CHROOT_INJECT_ARGS+=("$INJECT_FLAG" "$PWD/$ext_pkg")
    fi
done
shopt -u nullglob

# Helper function to parse build logs
parse_build_log() {
    local logfile="build.log"
    echo -e "\n\033[1;31m    [!] Build failed! Diagnosing missing dependencies...\033[0m"
    
    # 1. Check for Pacman missing dependencies (AUR packages needed)
    local pacman_missing
    pacman_missing=$(awk '/==> Missing dependencies:/{flag=1; next} /^==>/{flag=0} flag && /^  ->/ {print $2}' "$logfile")
    
    if [ -n "$pacman_missing" ]; then
        echo -e "\033[1;33m    Add these to AUR_DEPENDENCIES in this script (they are missing from the chroot):\033[0m"
        while read -r dep; do
            echo "      \"$dep\""
        done <<< "$pacman_missing"
    fi

    # 2. Check for Python PEP-517 missing dependencies (Missing from PKGBUILD)
    local python_missing
    python_missing=$(awk '/ERROR Missing dependencies:/{flag=1; next} /^==> ERROR:/{flag=0} flag && /^[[:space:]]/ {print $1}' "$logfile")
    
    if [ -n "$python_missing" ]; then
        echo -e "\033[1;33m    Add these to 'makedepends' (and likely 'depends') in your PKGBUILD:\033[0m"
        while read -r dep; do
            # Strip constraint versions (<, >, =, ~) for cleaner copy-pasting
            clean_dep=$(echo "$dep" | sed -E 's/[<>=~].*//')
            echo "      '$clean_dep'    (Raw constraint: $dep)"
        done <<< "$python_missing"
    fi
    echo ""
}

# ==============================================================================
# PHASE 0: BUILD AUR DEPENDENCIES
# ==============================================================================
echo -e "\n\033[1;34m==> Phase 0: Resolving external AUR dependencies...\033[0m"
for entry in "${AUR_DEPENDENCIES[@]}"; do
    # Parse entry for optional missing dependencies (format: pkgname:dep1 dep2)
    IFS=':' read -r dep missing_deps <<< "$entry"

    shopt -s nullglob
    existing_pkgs=("${dep}"-*.pkg.tar.zst)
    shopt -u nullglob

    if [ ${#existing_pkgs[@]} -gt 0 ]; then
        echo -e "\033[1;32m -> Pre-built package for $dep found in root, skipping build.\033[0m"
        continue
    fi

    echo -e "\n\033[1;33m -> Fetching and building AUR dependency: $dep\033[0m"
    if [ ! -d "$dep" ]; then
        git clone "https://aur.archlinux.org/${dep}.git"
    fi

    cd "$dep"

    # Dynamically patch the PKGBUILD if missing dependencies were specified
    if [ -n "$missing_deps" ]; then
        echo -e "\033[1;35m -> Patching PKGBUILD for $dep with missing dependencies: $missing_deps\033[0m"
        formatted_deps=""
        for md in $missing_deps; do formatted_deps="$formatted_deps '$md'"; done
        echo -e "\n# --- Injected by push-to-aur.sh ---\nmakedepends+=($formatted_deps)\ndepends+=($formatted_deps)" >> PKGBUILD
    fi

    set +e
    "${BUILD_CMD[@]}" "${CHROOT_INJECT_ARGS[@]}" 2>&1 | tee build.log
    BUILD_STATUS=${PIPESTATUS[0]}
    set -e

    if [ $BUILD_STATUS -ne 0 ]; then
        parse_build_log
        FAILED_PACKAGES+=("$dep (AUR Dependency)")
        cd ..
        continue
    fi

    shopt -s nullglob
    built_pkgs=(*.pkg.tar.zst)
    shopt -u nullglob

    for pkg_file in "${built_pkgs[@]}"; do
        echo " -> Adding $pkg_file to injection list."
        # Copy to root so subsequent script runs find it immediately
        cp "$pkg_file" ../
        CHROOT_INJECT_ARGS+=("$INJECT_FLAG" "$PWD/$pkg_file")
    done
    cd ..
done

# ==============================================================================
# PHASE 1: BUILD LOCAL PACKAGES
# ==============================================================================
echo -e "\n\033[1;34m==> Phase 1: Building target packages in clean chroot...\033[0m"
for pkg in "${PACKAGES[@]}"; do
    if [ -d "$pkg" ]; then
        echo -e "\n\033[1;36m -> Testing $pkg in clean chroot\033[0m"
        cd "$pkg"

        namcap PKGBUILD || true

        set +e
        "${BUILD_CMD[@]}" "${CHROOT_INJECT_ARGS[@]}" 2>&1 | tee build.log
        BUILD_STATUS=${PIPESTATUS[0]}
        set -e

        if [ $BUILD_STATUS -ne 0 ]; then
            parse_build_log
            FAILED_PACKAGES+=("$pkg")
            cd ..
            continue
        fi

        SUCCESS_PACKAGES+=("$pkg")

        shopt -s nullglob
        built_pkgs=(*.pkg.tar.zst)
        shopt -u nullglob

        for pkg_file in "${built_pkgs[@]}"; do
            namcap "$pkg_file" || true
            CHROOT_INJECT_ARGS+=("$INJECT_FLAG" "$PWD/$pkg_file")
        done

        cd ..
    fi
done

# ==============================================================================
# SUMMARY REPORT
# ==============================================================================
echo -e "\n\033[1;34m========================================\033[0m"
echo -e "\033[1;34m           BUILD SUMMARY                \033[0m"
echo -e "\033[1;34m========================================\033[0m"

if [ ${#SUCCESS_PACKAGES[@]} -gt 0 ]; then
    echo -e "\033[1;32mSuccessful Packages:\033[0m"
    for sp in "${SUCCESS_PACKAGES[@]}"; do echo "  - $sp"; done
fi

if [ ${#FAILED_PACKAGES[@]} -gt 0 ]; then
    echo -e "\n\033[1;31mFailed Packages (Check logs above for missing deps):\033[0m"
    for fp in "${FAILED_PACKAGES[@]}"; do echo "  - $fp"; done
    echo -e "\n\033[1;33mPlease fix the failed packages and run the script again.\033[0m"
else
    echo -e "\n\033[1;32mAll packages built successfully!\033[0m"
fi
