import pytest
import os
import json
from datetime import datetime
from aur_python_packer.state import StateManager


def test_update_package_injected_depends(tmp_path):
    """update_package records injected_depends in the state entry."""
    state_file = os.path.join(str(tmp_path), "build_index.json")
    sm = StateManager(state_file)

    sm.update_package(
        "pkg-a",
        "1.0.0",
        "success",
        skipped_checks=False,
        injected_depends=["python-bar", "python-baz"],
    )

    pkg = sm.get_package("pkg-a")
    assert pkg["status"] == "success"
    assert pkg["version"] == "1.0.0"
    assert pkg["injected_depends"] == ["python-bar", "python-baz"]


def test_update_package_no_injected(tmp_path):
    """update_package without injected_depends does not add the field."""
    state_file = os.path.join(str(tmp_path), "build_index.json")
    sm = StateManager(state_file)

    sm.update_package("pkg-b", "2.0.0", "success")

    pkg = sm.get_package("pkg-b")
    assert "injected_depends" not in pkg


def test_update_package_injected_empty_list(tmp_path):
    """Empty injected_depends list is not stored."""
    state_file = os.path.join(str(tmp_path), "build_index.json")
    sm = StateManager(state_file)

    sm.update_package("pkg-c", "3.0.0", "success", injected_depends=[])

    pkg = sm.get_package("pkg-c")
    assert "injected_depends" not in pkg


def test_state_persists_to_disk(tmp_path):
    """State is saved to disk and can be reloaded."""
    state_file = os.path.join(str(tmp_path), "build_index.json")
    sm = StateManager(state_file)

    sm.update_package(
        "pkg-d",
        "4.0.0",
        "success",
        injected_depends=["extra-dep"],
    )

    # Reload from disk
    sm2 = StateManager(state_file)
    pkg = sm2.get_package("pkg-d")
    assert pkg["injected_depends"] == ["extra-dep"]
