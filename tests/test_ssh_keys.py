# SPDX-FileCopyrightText: © 2025
# SPDX-License-Identifier: MIT

import pytest

from scripts.ssh_keys import generate_ssh_key


@pytest.mark.parametrize("key_type", ["rsa", "dsa", "ecdsa", "ed25519"])
def test_generate_ssh_key(key_type, tmp_path):
    """Test that SSH key generation creates the expected key file."""
    key_path = tmp_path / "test_keys"
    key_path.mkdir(parents=True, exist_ok=True)

    result = generate_ssh_key(str(key_path), key_type)

    assert result == 0, f"ssh-keygen failed for key type {key_type}"
    key_file = key_path / f"id_{key_type}"
    assert key_file.exists(), f"Expected key file {key_file} not found"


def test_generate_ssh_key_missing_ssh_keygen(monkeypatch, tmp_path):
    """Test graceful error when ssh-keygen is not in PATH."""
    monkeypatch.setenv("PATH", "/nonexistent")

    key_path = tmp_path / "test_keys"
    key_path.mkdir(parents=True, exist_ok=True)

    result = generate_ssh_key(str(key_path), "rsa")

    assert result == 1
