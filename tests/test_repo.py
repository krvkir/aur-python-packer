import os
from unittest.mock import patch
from aur_python_packer.repo import RepoManager

def test_add_to_repo(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    pkg_file = tmp_path / "test-1.0-1-any.pkg.tar.zst"
    pkg_file.write_text("package content")
    
    with patch('aur_python_packer.repo.run_command') as mock_run:
        mgr = RepoManager(str(repo_dir))
        mgr.add_package(str(pkg_file))
        
        assert (repo_dir / "test-1.0-1-any.pkg.tar.zst").exists()
        assert mock_run.call_count == 2
        args = mock_run.call_args_list[1][0][0]
        assert "repo-add" in args
        assert str(repo_dir / "localrepo.db.tar.gz") in args
