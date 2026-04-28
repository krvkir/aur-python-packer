import pytest
import os
# from aur_python_packer.metadata import MetadataParser  # This will fail

def test_parse_srcinfo_simple(tmp_path):
    srcinfo = """
pkgbase = python-test
	pkgname = python-test
	pkgver = 1.0.0
	pkgrel = 1
	url = http://test.com
	arch = any
	license = MIT
	depends = python-requests
	depends = python-urllib3
    """
    path = tmp_path / ".SRCINFO"
    path.write_text(srcinfo)
    
    from aur_python_packer.metadata import MetadataParser
    parser = MetadataParser()
    meta = parser.parse_srcinfo(str(path))
    
    assert meta["pkgname"] == "python-test"
    assert "python-requests" in meta["depends"]
    assert "python-urllib3" in meta["depends"]

def test_parse_pkgbuild_simple(tmp_path):
    pkgbuild = """
pkgname=python-test
pkgver=1.0.0
depends=('python-requests' 'python-urllib3')
    """
    path = tmp_path / "PKGBUILD"
    path.write_text(pkgbuild)
    
    from aur_python_packer.metadata import MetadataParser
    parser = MetadataParser()
    meta = parser.parse_pkgbuild(str(path))
    
    assert meta["pkgname"] == "python-test"
    assert "python-requests" in meta["depends"]
    assert "python-urllib3" in meta["depends"]
