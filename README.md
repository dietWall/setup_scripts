# setup_scripts
contains some of my scripts to start development faster.
Since my build and development environment is getting bigger, I wanted to have some reproducible scripts for setting up SSH connections and installing software.
In future, I plan to extend this repo with some additional, reusable functions on demand, so I don't have to remind how to do this repeating tasks.

# ssh-keys

Generates SSH keys on a client PC and deploys them to the build/server PC.

## Options

| Flag | Description |
|------|-------------|
| `--generate` | Generate a new SSH key of the specified type (`rsa`, `dsa`, `ecdsa`, `ed25519`) |
| `--key-path` | Directory where keys are stored/generated (defaults to `~/.ssh`) |
| `--deploy-to-host` | Deploys the public key to `<user>@<host>` via SSH |
| `--password_type` | Password input type: `prompt` or `dotenv` |
| `--dotenv-file` | Path to `.env` file containing `PASSWORD=yourpassword` |

## Usage

### Generate a new SSH key

```bash
ssh-keys --generate rsa --key-path ~/.ssh
```

### Deploy an existing key

If a key already exists in `--key-path`, it is detected automatically — no `--generate` needed:

```bash
ssh-keys --deploy-to-host user@host --key-path ~/.ssh
```

### Generate and deploy in one step

```bash
ssh-keys --generate ed25519 --key-path ~/.ssh --deploy-to-host user@host
```

### Deploy with a dotenv password file

```bash
ssh-keys --deploy-to-host user@host --password_type dotenv --dotenv-file /path/to/.env
```

The `.env` file requires just one line:

```
PASSWORD=yourpassword
```

## How it works

- **Key generation**: uses `ssh-keygen` to create keys in `--key-path`.
- **Deployment**: uses `paramiko` to copy the public key to `~/.ssh/authorized_keys` on the remote host.
- **Key detection**: when `--deploy-to-host` is used without `--generate`, the script scans `--key-path` for existing `.pub` files (`id_rsa.pub`, `id_ed25519.pub`, etc.) to determine the key type automatically.
- **Password**: prompted interactively by default, or read from a `.env` file when `--password_type dotenv` is specified.

# Testing

Tests are implemented in `tests/` directory.

To install development dependencies (`pytest`, `python-dotenv` etc.):

```bash
pip install -e ".[dev]"
```

To run tests:

```bash
pytest
```

Or with coverage reporting:

```bash
pytest --cov=scripts --cov-report=term-missing
```

To build the package:

```bash
pip install build
python -m build
```

# Improvements / Nice to have

If you have any suggestions to improve code/tests, feel free to create a PR for the scripts or write me a message.
More specifically:
- I want to test password prompt automatically.
- add a connection check at the end of test_ssh_keys_deployment.
