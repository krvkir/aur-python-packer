import pytest
from unittest.mock import patch
# from aur_python_packer.clients import PyPIClient, AURClient # This will fail

def test_pypi_client_get_meta():
    from aur_python_packer.clients import PyPIClient
    client = PyPIClient()
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "info": {
                "name": "requests",
                "version": "2.31.0",
                "summary": "Summary",
                "requires_dist": ["idna"]
            }
        }
        
        meta = client.get_metadata("requests")
        assert meta["name"] == "requests"
        assert meta["version"] == "2.31.0"

def test_aur_client_get_info():
    from aur_python_packer.clients import AURClient
    client = AURClient()
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "resultcount": 1,
            "results": [{"Name": "python-requests", "Version": "2.31.0"}]
        }
        
        info = client.get_info("python-requests")
        assert info["Name"] == "python-requests"
        assert info["Version"] == "2.31.0"
