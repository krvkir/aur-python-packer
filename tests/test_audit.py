import pytest
from unittest.mock import patch
from aur_python_packer.audit import Auditor

def test_audit_outdated():
    state = {
        "packages": {
            "python-requests": {"version": "2.30.0"}
        }
    }
    
    with patch('aur_python_packer.generator.PyPIGenerator.fetch_meta') as mock_fetch:
        mock_fetch.return_value = {"version": "2.31.0"}
        
        auditor = Auditor(state)
        report = auditor.audit()
        
        assert "python-requests" in report
        assert report["python-requests"]["current"] == "2.30.0"
        assert report["python-requests"]["latest"] == "2.31.0"
        assert report["python-requests"]["outdated"] is True
