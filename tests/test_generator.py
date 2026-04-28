import pytest
from unittest.mock import patch
from aur_python_packer.generator import PyPIGenerator

@patch('requests.get')
def test_fetch_pypi_meta(mock_get):
    mock_get.return_value.json.return_value = {
        "info": {
            "name": "requests",
            "version": "2.31.0",
            "summary": "Python HTTP for Humans.",
            "license": "Apache 2.0",
            "home_page": "https://requests.readthedocs.io",
            "requires_dist": ["charset-normalizer", "idna"]
        }
    }
    mock_get.return_value.status_code = 200
    
    gen = PyPIGenerator()
    # Now fetch_meta is gone, but generator uses client.get_metadata internally.
    meta = gen.pypi_client.get_metadata("requests")
    assert meta['name'] == "requests"
    assert meta['version'] == "2.31.0"
    assert meta['requires_dist'] == ["charset-normalizer", "idna"]

def test_render_pkgbuild():
    gen = PyPIGenerator()
    meta = {
        "pkgname": "python-test",
        "pkgver": "1.0.0",
        "pkgdesc": "A test package",
        "url": "http://test.com",
        "license": "MIT",
        "sha256": "abcdef123456",
        "depends": ["python-requests"]
    }
    content = gen.render(meta)
    assert 'pkgname=python-test' in content
    assert 'pkgver=1.0.0' in content
    assert "sha256sums=('abcdef123456')" in content
