import pytest
import os
# from aur_python_packer.config import PacmanConfig # This will fail

def test_generate_custom_conf(tmp_path):
    from aur_python_packer.config import PacmanConfig
    
    base_conf = tmp_path / "base.conf"
    base_conf.write_text("[options]\nHoldPkg = pacman glibc\n[core]\nInclude = /etc/pacman.d/mirrorlist")
    
    config = PacmanConfig(
        repo_dir="/tmp/repo",
        db_name="localrepo",
        db_path_override="/tmp/db",
        cache_path_override="/tmp/cache"
    )
    
    output_path = tmp_path / "custom.conf"
    config.generate(base_conf=str(base_conf), output_path=str(output_path))
    
    content = output_path.read_text()
    assert "[localrepo]" in content
    assert "Server = file:///tmp/repo" in content
    assert "DBPath = /tmp/db" in content
    assert "CacheDir = /tmp/cache" in content
    assert "SigLevel = Never" in content
    assert "XferCommand" in content
