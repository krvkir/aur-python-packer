import pytest
import os
from unittest.mock import patch, MagicMock
# from aur_python_packer.sandbox import Sandbox # This will fail

def test_sandbox_command_construction():
    from aur_python_packer.sandbox import Sandbox
    
    with patch('os.getuid', return_value=1000), \
         patch('os.getgid', return_value=1000), \
         patch('os.getlogin', return_value='testuser'), \
         patch('os.cpu_count', return_value=4):
        
        sb = Sandbox(work_dir="/tmp/work", root_dir="/tmp/root")
        cmd = sb.get_bwrap_command(
            ["ls"], 
            cwd="/tmp/work/build", 
            custom_conf="/tmp/pacman.conf", 
            pacman_db_path="/tmp/db"
        )
        
        assert "bwrap" in cmd
        assert "--bind" in cmd
        assert "/tmp/root" in cmd
        assert "ls" in cmd
        assert "MAKEFLAGS=-j4" in [arg for arg in cmd if arg.startswith("MAKEFLAGS=")] or any("MAKEFLAGS" in arg for arg in cmd)

def test_sandbox_run(tmp_path):
    from aur_python_packer.sandbox import Sandbox
    
    with patch('aur_python_packer.sandbox.run_command') as mock_run:
        sb = Sandbox(work_dir=str(tmp_path), root_dir=str(tmp_path/"root"))
        sb.run(["true"], cwd=str(tmp_path), custom_conf="conf", pacman_db_path="db")
        assert mock_run.called
