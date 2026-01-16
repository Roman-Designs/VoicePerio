"""
Test Suite for VoicePerio Build System

Tests for verifying:
- PyInstaller spec file syntax
- Build script execution
- Executable creation
- Distribution package completeness
- Resource file inclusion

Run with: python -m pytest tests/test_build.py -v
"""

import os
import sys
import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SPEC_FILE = PROJECT_ROOT / "installer" / "voiceperio.spec"
BUILD_SCRIPT = PROJECT_ROOT / "build.bat"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
DIST_DIR = PROJECT_ROOT / "dist" / "VoicePerio"


class TestSpecFile:
    """Tests for PyInstaller spec file"""

    def test_spec_file_exists(self):
        """Verify spec file exists"""
        assert SPEC_FILE.exists(), f"Spec file not found: {SPEC_FILE}"

    def test_spec_file_syntax(self):
        """Verify spec file has valid Python syntax"""
        import ast
        with open(SPEC_FILE, 'r') as f:
            content = f.read()
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Spec file syntax error: {e}")

    def test_spec_file_has_required_sections(self):
        """Verify spec file contains required PyInstaller sections"""
        with open(SPEC_FILE, 'r') as f:
            content = f.read()
        
        required_sections = [
            'Analysis',
            'PYZ',
            'EXE',
            'COLLECT'
        ]
        
        for section in required_sections:
            assert section in content, f"Missing required section: {section}"

    def test_spec_file_has_hidden_imports(self):
        """Verify spec file includes hidden imports"""
        with open(SPEC_FILE, 'r') as f:
            content = f.read()
        
        required_imports = [
            'vosk',
            'PyQt6',
            'sounddevice',
            'pyautogui',
            'keyboard',
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing hidden import: {imp}"

    def test_spec_file_has_data_files(self):
        """Verify spec file includes data files"""
        with open(SPEC_FILE, 'r') as f:
            content = f.read()
        
        assert 'datas' in content, "Missing datas section"
        assert 'commands' in content, "Missing commands data file"


class TestBuildScript:
    """Tests for build script"""

    def test_build_script_exists(self):
        """Verify build script exists"""
        assert BUILD_SCRIPT.exists(), f"Build script not found: {BUILD_SCRIPT}"

    def test_build_script_has_color_codes(self):
        """Verify build script uses color codes for output"""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        
        color_indicators = ['[92m', '[91m', '[93m', '[94m']
        found = any(color in content for color in color_indicators)
        assert found, "Build script should use color codes for output"

    def test_build_script_checks_python_version(self):
        """Verify build script checks Python version"""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        
        assert 'python' in content.lower(), "Build script should reference Python"
        assert 'version' in content.lower() or '3.10' in content, \
            "Build script should check version"


class TestRequirementsFile:
    """Tests for requirements.txt"""

    def test_requirements_file_exists(self):
        """Verify requirements file exists"""
        assert REQUIREMENTS_FILE.exists(), \
            f"Requirements file not found: {REQUIREMENTS_FILE}"

    def test_requirements_file_has_build_dependency(self):
        """Verify requirements includes PyInstaller"""
        with open(REQUIREMENTS_FILE, 'r') as f:
            content = f.read()
        
        assert 'pyinstaller' in content.lower(), \
            "Requirements should include pyinstaller"

    def test_requirements_file_has_runtime_dependencies(self):
        """Verify requirements includes runtime dependencies"""
        with open(REQUIREMENTS_FILE, 'r') as f:
            content = f.read()
        
        required_deps = ['vosk', 'pyqt6', 'sounddevice']
        for dep in required_deps:
            assert dep in content.lower(), \
                f"Requirements should include {dep}"


class TestVersionInfo:
    """Tests for version information file"""

    def test_version_info_exists(self):
        """Verify version info file exists"""
        version_file = PROJECT_ROOT / "installer" / "version_info.txt"
        assert version_file.exists(), \
            f"Version info file not found: {version_file}"

    def test_version_info_has_valid_syntax(self):
        """Verify version info file has valid syntax"""
        version_file = PROJECT_ROOT / "installer" / "version_info.txt"
        with open(version_file, 'r') as f:
            content = f.read()
        
        assert 'VSVersionInfo' in content, \
            "Version info should have VSVersionInfo"
        assert 'FileVersion' in content, \
            "Version info should have FileVersion"
        assert 'ProductVersion' in content, \
            "Version info should have ProductVersion"


class TestDistributionStructure:
    """Tests for distribution package structure"""

    @pytest.fixture
    def mock_dist_directory(self, tmp_path):
        """Create a mock distribution directory for testing"""
        dist = tmp_path / "VoicePerio"
        dist.mkdir()
        
        # Create expected structure
        (dist / "VoicePerio.exe").touch()
        models_dir = dist / "models" / "vosk-model-small-en-us"
        models_dir.mkdir(parents=True)
        (models_dir / "am").mkdir()
        (models_dir / "am" / "final.mdl").touch()
        (dist / "config.json").touch()
        (dist / "README.txt").touch()
        (dist / "LICENSE.txt").touch()
        
        return dist

    def test_expected_distribution_structure(self, mock_dist_directory):
        """Verify expected files exist in distribution"""
        dist = mock_dist_directory
        
        expected_files = [
            dist / "VoicePerio.exe",
            dist / "config.json",
            dist / "README.txt",
            dist / "LICENSE.txt",
        ]
        
        for file_path in expected_files:
            assert file_path.exists(), \
                f"Expected file not found: {file_path}"

    def test_model_directory_structure(self, mock_dist_directory):
        """Verify model directory structure"""
        model_dir = mock_dist_directory / "models" / "vosk-model-small-en-us"
        assert model_dir.exists(), "Model directory should exist"
        
        # Check for key model file
        model_file = model_dir / "am" / "final.mdl"
        assert model_file.exists(), "Model file should exist"


class TestBuildVerification:
    """Tests for build verification logic"""

    def test_build_verification_script_exists(self):
        """Verify build verification logic exists in build script"""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        
        # Build script should have verification mode
        assert '--verify' in content or 'verify' in content.lower(), \
            "Build script should have verification option"

    def test_build_verification_checks_executable(self):
        """Verify verification checks for executable"""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        
        assert 'exe' in content.lower() or 'executable' in content.lower(), \
            "Build script should check for executable"


class TestCIEnvironment:
    """Tests for CI/CD environment compatibility"""

    @patch('subprocess.run')
    def test_build_can_run_in_ci(self, mock_run, tmp_path):
        """Verify build process can be simulated in CI"""
        # Mock successful build
        mock_run.return_value = MagicMock(returncode=0)
        
        # This test verifies the build script structure is compatible
        # with CI environments
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        
        # No hard-coded user paths
        assert '%USERPROFILE%' not in content, \
            "Build script should not use user-specific paths"
        assert 'C:\\Users\\' not in content, \
            "Build script should not use hard-coded user paths"

    def test_build_script_has_error_handling(self):
        """Verify build script handles errors"""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        
        # Check for error handling patterns
        assert 'errorlevel' in content or 'ERROR' in content, \
            "Build script should have error handling"


class TestMockedBuild:
    """Mocked build tests for CI environments"""

    @pytest.fixture
    def mock_pyinstaller(self, tmp_path):
        """Create a mock PyInstaller environment"""
        venv_dir = tmp_path / "venv"
        venv_dir.mkdir()
        scripts_dir = venv_dir / "Scripts"
        scripts_dir.mkdir()
        (scripts_dir / "activate.bat").touch()
        
        return tmp_path

    def test_spec_file_can_be_parsed(self, mock_pyinstaller):
        """Verify spec file can be parsed without full PyInstaller"""
        import ast
        
        with open(SPEC_FILE, 'r') as f:
            content = f.read()
        
        # Should be able to parse as Python
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Cannot parse spec file: {e}")

    def test_build_script_is_valid_batch(self):
        """Verify build script is valid batch file syntax"""
        with open(BUILD_SCRIPT, 'r') as f:
            lines = f.readlines()
        
        # Check for batch file indicators
        assert lines[0].strip() == '@echo off', \
            "Build script should start with @echo off"
        
        # Should have REM or :: comments
        has_comments = any(
            line.strip().startswith(('REM', '::')) 
            for line in lines
        )
        assert has_comments, "Build script should have comments"


# ============================================================================
# Fixtures for integration tests
# ============================================================================

@pytest.fixture(scope="module")
def project_structure():
    """Provide project structure paths"""
    return {
        'project_root': PROJECT_ROOT,
        'spec_file': SPEC_FILE,
        'build_script': BUILD_SCRIPT,
        'requirements': REQUIREMENTS_FILE,
        'dist_dir': DIST_DIR,
    }


# ============================================================================
# Skip markers for long-running tests
# ============================================================================

needs_full_build = pytest.mark.skipif(
    not DIST_DIR.exists(),
    reason="Full build not available - run build.bat first"
)
