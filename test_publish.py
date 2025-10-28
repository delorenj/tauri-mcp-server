#!/usr/bin/env python3
"""
Test suite for publish.py script.

Run with: python -m pytest test_publish.py -v
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import modules from publish.py
import sys
sys.path.insert(0, str(Path(__file__).parent))

from publish import (
    BumpType,
    PackageInfo,
    PublishTarget,
    check_git_clean,
    check_npm_credentials,
    get_otp_from_1password,
    get_packages,
    PROJECT_ROOT,
)


class TestPackageInfo:
    """Test PackageInfo class functionality."""

    @pytest.fixture
    def temp_package_json(self, tmp_path):
        """Create a temporary package.json file."""
        package_data = {
            "name": "test-package",
            "version": "1.2.3",
            "description": "Test package"
        }
        package_path = tmp_path / "package.json"
        with open(package_path, "w") as f:
            json.dump(package_data, f)
        return package_path

    def test_load_package_json(self, temp_package_json, tmp_path):
        """Test loading package.json data."""
        pkg = PackageInfo("Test", tmp_path, temp_package_json)
        assert pkg.npm_name == "test-package"
        assert pkg.version == "1.2.3"

    def test_bump_version_patch(self, temp_package_json, tmp_path):
        """Test patch version bump."""
        pkg = PackageInfo("Test", tmp_path, temp_package_json)
        new_version = pkg.bump_version(BumpType.PATCH)
        assert new_version == "1.2.4"

    def test_bump_version_minor(self, temp_package_json, tmp_path):
        """Test minor version bump."""
        pkg = PackageInfo("Test", tmp_path, temp_package_json)
        new_version = pkg.bump_version(BumpType.MINOR)
        assert new_version == "1.3.0"

    def test_bump_version_major(self, temp_package_json, tmp_path):
        """Test major version bump."""
        pkg = PackageInfo("Test", tmp_path, temp_package_json)
        new_version = pkg.bump_version(BumpType.MAJOR)
        assert new_version == "2.0.0"

    def test_update_version(self, temp_package_json, tmp_path):
        """Test updating package.json version."""
        pkg = PackageInfo("Test", tmp_path, temp_package_json)
        pkg.update_version("2.0.0", dry_run=False)

        # Verify file was updated
        with open(temp_package_json, "r") as f:
            data = json.load(f)
        assert data["version"] == "2.0.0"

    def test_update_version_dry_run(self, temp_package_json, tmp_path):
        """Test dry run doesn't modify package.json."""
        pkg = PackageInfo("Test", tmp_path, temp_package_json)
        pkg.update_version("2.0.0", dry_run=True)

        # Verify file was NOT updated
        with open(temp_package_json, "r") as f:
            data = json.load(f)
        assert data["version"] == "1.2.3"


class TestVersionBumping:
    """Test version bumping logic."""

    @pytest.mark.parametrize("current,bump,expected", [
        ("0.1.0", BumpType.PATCH, "0.1.1"),
        ("0.1.0", BumpType.MINOR, "0.2.0"),
        ("0.1.0", BumpType.MAJOR, "1.0.0"),
        ("1.2.3", BumpType.PATCH, "1.2.4"),
        ("1.2.3", BumpType.MINOR, "1.3.0"),
        ("1.2.3", BumpType.MAJOR, "2.0.0"),
        ("10.20.30", BumpType.PATCH, "10.20.31"),
        ("10.20.30", BumpType.MINOR, "10.21.0"),
        ("10.20.30", BumpType.MAJOR, "11.0.0"),
    ])
    def test_version_bumping(self, current, bump, expected, tmp_path):
        """Test various version bumping scenarios."""
        package_data = {"name": "test", "version": current}
        package_path = tmp_path / "package.json"
        with open(package_path, "w") as f:
            json.dump(package_data, f)

        pkg = PackageInfo("Test", tmp_path, package_path)
        assert pkg.bump_version(bump) == expected


class TestGitOperations:
    """Test git-related functions."""

    @patch('subprocess.run')
    def test_check_git_clean_true(self, mock_run):
        """Test git clean check when directory is clean."""
        mock_run.return_value = Mock(stdout="", returncode=0)
        assert check_git_clean() is True

    @patch('subprocess.run')
    def test_check_git_clean_false(self, mock_run):
        """Test git clean check when directory has changes."""
        mock_run.return_value = Mock(stdout="M file.txt\n", returncode=0)
        assert check_git_clean() is False

    @patch('subprocess.run')
    def test_check_git_clean_error(self, mock_run):
        """Test git clean check when git command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        # Should return True and continue (with warning)
        assert check_git_clean() is True


class TestNpmOperations:
    """Test npm-related functions."""

    @patch('subprocess.run')
    def test_check_npm_credentials_logged_in(self, mock_run):
        """Test npm credentials check when logged in."""
        mock_run.return_value = Mock(stdout="delorenj\n", returncode=0)
        assert check_npm_credentials() is True

    @patch('subprocess.run')
    def test_check_npm_credentials_not_logged_in(self, mock_run):
        """Test npm credentials check when not logged in."""
        mock_run.return_value = Mock(stdout="", returncode=1)
        assert check_npm_credentials() is False

    @patch('subprocess.run')
    def test_check_npm_credentials_npm_not_found(self, mock_run):
        """Test npm credentials check when npm is not installed."""
        mock_run.side_effect = FileNotFoundError()
        assert check_npm_credentials() is False


class TestOnePasswordIntegration:
    """Test 1Password OTP integration."""

    @patch('subprocess.run')
    def test_get_otp_success(self, mock_run):
        """Test successful OTP retrieval from 1Password."""
        mock_run.return_value = Mock(stdout="123456\n", returncode=0)
        otp = get_otp_from_1password()
        assert otp == "123456"

    @patch('subprocess.run')
    def test_get_otp_failure(self, mock_run):
        """Test failed OTP retrieval from 1Password."""
        mock_run.return_value = Mock(stdout="", returncode=1)
        otp = get_otp_from_1password()
        assert otp is None

    @patch('subprocess.run')
    def test_get_otp_cli_not_found(self, mock_run):
        """Test OTP retrieval when 1Password CLI is not installed."""
        mock_run.side_effect = FileNotFoundError()
        otp = get_otp_from_1password()
        assert otp is None


class TestPublishTargets:
    """Test package target selection."""

    def test_get_packages_plugin(self):
        """Test getting plugin package."""
        packages = get_packages(PublishTarget.PLUGIN)
        assert len(packages) == 1
        assert packages[0].name == "Tauri Plugin"

    def test_get_packages_mcp(self):
        """Test getting MCP package."""
        packages = get_packages(PublishTarget.MCP)
        assert len(packages) == 1
        assert packages[0].name == "MCP Server"

    def test_get_packages_all(self):
        """Test getting all packages."""
        packages = get_packages(PublishTarget.ALL)
        assert len(packages) == 2
        names = [pkg.name for pkg in packages]
        assert "Tauri Plugin" in names
        assert "MCP Server" in names


class TestEnums:
    """Test enum types."""

    def test_bump_type_values(self):
        """Test BumpType enum values."""
        assert BumpType.PATCH.value == "patch"
        assert BumpType.MINOR.value == "minor"
        assert BumpType.MAJOR.value == "major"

    def test_publish_target_values(self):
        """Test PublishTarget enum values."""
        assert PublishTarget.PLUGIN.value == "plugin"
        assert PublishTarget.MCP.value == "mcp"
        assert PublishTarget.ALL.value == "all"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_package_info_invalid_json(self, tmp_path):
        """Test PackageInfo with invalid JSON."""
        package_path = tmp_path / "package.json"
        with open(package_path, "w") as f:
            f.write("{ invalid json }")

        with pytest.raises(SystemExit):
            PackageInfo("Test", tmp_path, package_path)

    def test_package_info_missing_file(self, tmp_path):
        """Test PackageInfo with missing file."""
        package_path = tmp_path / "nonexistent.json"

        with pytest.raises(SystemExit):
            PackageInfo("Test", tmp_path, package_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--color=yes"])
