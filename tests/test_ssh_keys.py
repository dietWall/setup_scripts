# SPDX-FileCopyrightText: © 2025
# SPDX-License-Identifier: MIT

from unittest.mock import MagicMock, patch

import pytest

from scripts.ssh_keys import deploy, generate_ssh_key, get_key_type_from_path, password_prompt, add_to_ssh_config, test_ssh_config as validate_ssh_config


@pytest.mark.parametrize("key_type", ["rsa", "dsa", "ecdsa", "ed25519"])
def test_generate_ssh_key(key_type, tmp_path):
    """Test that SSH key generation creates the expected key file."""
    key_path = tmp_path / "test_keys"
    key_path.mkdir(parents=True, exist_ok=True)

    result = generate_ssh_key(str(key_path), key_type)

    assert result == 0, f"ssh-keygen failed for key type {key_type}"
    priv_key = key_path / f"id_{key_type}"
    pub_key = key_path / f"id_{key_type}.pub"
    assert priv_key.exists(), f"Expected private key file {priv_key} not found"
    assert pub_key.exists(), f"Expected public key file {pub_key} not found"
    pub_content = pub_key.read_text().strip()
    assert pub_content, f"Public key {pub_key} is empty"
    assert len(pub_content.split()) == 3, f"Public key {pub_key} has invalid format"
    assert priv_key.read_text().startswith("-----BEGIN"), f"Private key {priv_key} has invalid format"


def test_generate_ssh_key_missing_ssh_keygen(monkeypatch, tmp_path):
    """Test graceful error when ssh-keygen is not in PATH."""
    monkeypatch.setenv("PATH", "/nonexistent")

    key_path = tmp_path / "test_keys"
    key_path.mkdir(parents=True, exist_ok=True)

    result = generate_ssh_key(str(key_path), "rsa")

    assert result == 1


def test_generate_ssh_key_missing_key_type(tmp_path):
    """Test graceful error when key_type is empty."""
    key_path = tmp_path / "test_keys"
    key_path.mkdir(parents=True, exist_ok=True)

    result = generate_ssh_key(str(key_path), "")

    assert result == 1


def test_generate_ssh_key_missing_directory(tmp_path):
    """Test graceful error when directory does not exist."""
    result = generate_ssh_key(str(tmp_path / "nonexistent"), "rsa")

    assert result == 1


def test_get_filename_with_existing_files(tmp_path):
    """Test that get_filename increments suffix when files already exist."""
    from scripts.ssh_keys import get_filename

    key_path = tmp_path / "test_keys"
    key_path.mkdir(parents=True, exist_ok=True)

    (key_path / "id_rsa").touch()
    result = get_filename(str(key_path), "rsa")
    assert result == str(key_path / "id_rsa_1")

    (key_path / "id_rsa_1").touch()
    result = get_filename(str(key_path), "rsa")
    assert result == str(key_path / "id_rsa_2")


@pytest.mark.parametrize("key_type", ["rsa", "dsa", "ecdsa", "ed25519"])
def test_get_key_type_from_path(key_type, tmp_path):
    """Test that get_key_type_from_path detects existing key types."""
    key_path = tmp_path / "test_keys"
    key_path.mkdir(parents=True, exist_ok=True)

    (key_path / f"id_{key_type}.pub").touch()
    result = get_key_type_from_path(str(key_path))

    assert result == key_type


def test_get_key_type_from_path_no_keys(tmp_path):
    """Test that get_key_type_from_path returns None when no keys exist."""
    key_path = tmp_path / "test_keys"
    key_path.mkdir(parents=True, exist_ok=True)

    result = get_key_type_from_path(str(key_path))

    assert result is None


def test_password_prompt(monkeypatch):
    """Test that password_prompt returns the value from getpass."""
    from scripts.ssh_keys import password_prompt
    monkeypatch.setattr("getpass.getpass", lambda prompt="": "testpassword")

    result = password_prompt()

    assert result == "testpassword"


def test_deploy_invalid_host():
    """Test that deploy returns 1 when user_at_host has no @."""
    from scripts.ssh_keys import deploy

    result = deploy("/tmp/fake_key", "invalidhost", "password")

    assert result == 1


def test_deploy(tmp_path):
    """Test that deploy sends the correct commands via paramiko."""
    from scripts.ssh_keys import deploy

    key_file = tmp_path / "id_rsa.pub"
    key_file.write_text("ssh-rsa testkeycontent")

    mock_client = MagicMock()
    mock_channel = MagicMock()
    mock_client.exec_command.return_value = mock_channel

    with patch("paramiko.SSHClient", return_value=mock_client):
        result = deploy(str(key_file), "user@host", "password")

    assert result == 0
    mock_client.exec_command.assert_any_call("mkdir -p ~/.ssh/ && cat >> ~/.ssh/authorized_keys")
    mock_channel.stdin.write.assert_called_once_with(b"ssh-rsa testkeycontent")
    mock_channel.stdin.close.assert_called_once()
    mock_channel.recv_exit_status.assert_called_once()
    mock_client.exec_command.assert_any_call("chmod 644 ~/.ssh/authorized_keys && chmod 700 ~/.ssh/")


def test_add_to_ssh_config(monkeypatch, tmp_path):
    """Test that add_to_ssh_config creates a valid entry in ~/.ssh/config."""
    monkeypatch.setattr("scripts.ssh_keys.default_key_path", str(tmp_path))

    result = add_to_ssh_config("testhost", "testuser", str(tmp_path), "rsa")

    assert result == str(tmp_path / "config")
    config_path = tmp_path / "config"
    assert config_path.exists()
    content = config_path.read_text()
    assert "Host testhost" in content
    assert "HostName localhost" in content
    assert "User testuser" in content
    assert "IdentityFile" in content
    assert "id_rsa" in content


def test_add_to_ssh_config_appends(monkeypatch, tmp_path):
    """Test that add_to_ssh_config appends to an existing config file."""
    monkeypatch.setattr("scripts.ssh_keys.default_key_path", str(tmp_path))

    config_path = tmp_path / "config"
    config_path.write_text("Existing entry\n")

    result = add_to_ssh_config("testhost", "testuser", str(tmp_path), "ed25519")

    assert result == str(config_path)
    content = config_path.read_text()
    assert "Existing entry" in content
    assert "Host testhost" in content


def test_ssh_config(monkeypatch, tmp_path):
    """Test that test_ssh_config validates the config using ssh -G."""
    monkeypatch.setattr("scripts.ssh_keys.default_key_path", str(tmp_path))

    config_path = add_to_ssh_config("testhost", "testuser", str(tmp_path), "rsa")

    result = validate_ssh_config("testhost", config_path)

    assert result == 0
