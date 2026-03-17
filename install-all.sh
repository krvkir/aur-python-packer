#!/bin/bash
set -e

# Ordered list of packages based on their dependency graph
PACKAGES=(
    # Level 0 (No dependencies among these packages)
    # "python-jupyterlab-eventlistener"
    # "python-jupyterlab-cell-input-footer"
    # "python-jupyter-server-mcp"
    # "python-jupyterlab-chat"
    # "python-jupyter-ai-litellm"
    # "python-jupyterlab-notebook-awareness"
    # "python-jupyter-ai-tools"

    # Level 1
    # "python-jupyterlab-diff"             # depends on eventlistener, cell-input-footer
    # "python-jupyter-server-documents"    # depends on collaboration-ui
    # "python-jupyter-ai-router"           # depends on jupyterlab-chat
    # "python-jupyterlab-commands-toolkit" # depends on eventlistener

    # Level 2
    # "python-jupyter-ai-persona-manager"  # depends on jupyter-ai-router, jupyterlab-chat

    # Level 3
    # "python-jupyter-ai-chat-commands"    # depends on persona-manager, router, jupyterlab-chat
    # "python-jupyter-ai-jupyternaut"
    "python-jupyter-ai-magic-commands"
    "python-jupyter-ai"      # depends on persona-manager, server-documents, commands-toolkit, notebook-awareness, litellm, jupyterlab-chat
)

for pkg in "${PACKAGES[@]}"; do
    echo -e "\n\033[1;34m==> Building and installing: $pkg\033[0m"
    cd "$pkg"
    
    # Build and install the package, automatically resolving repo dependencies
    # and installing the built package without confirmation
    makepkg -si --noconfirm
    
    cd ..
done

echo -e "\n\033[1;32m==> All packages built and installed successfully!\033[0m"


