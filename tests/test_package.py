# SPDX-FileCopyrightText: © 2025
# SPDX-License-Identifier: MIT

import subprocess


def test_build_succeeds():
    """Test that building the package succeeds."""
    result = subprocess.run(['python', '-m', 'build'], capture_output=True, text=True)
    
    # Check exit code
    assert result.returncode == 0, \
        f"Build failed with code {result.returncode}"
    
    # Check if dist directory exists and has wheel files
    import os
    assert os.path.exists('dist'), "dist directory does not exist after build"
    assert any(f.endswith('.whl') for f in os.listdir('dist')), "No wheel files found"
    assert any(f.endswith('.tar.gz') for f in os.listdir('dist')), "No source tarballs found"


def test_ssh_keys_command_available():
    """Test that ssh-keys command is available and provides help."""
    # Force reinstall in development mode
    subprocess.run(['pip', 'uninstall', 'setup_scripts', '-y'], capture_output=True)
    subprocess.run(['pip', 'install', '-e', '.'], capture_output=True)
    
    # Test that ssh-keys command is available and works
    result = subprocess.run(['ssh-keys', '--help'], capture_output=True, text=True)
    
    # Check command exists (exit code 0)
    assert result.returncode == 0, \
        f"ssh-keys command failed with code {result.returncode}, stderr: {result.stderr}"
    
    # Check help output contains expected content
    help_output = result.stdout.lower()
    assert 'ssh-keygen' in help_output or 'usage' in help_output or 'deploy' in help_output, \
        f"Help output seems incomplete, output: {help_output}"
