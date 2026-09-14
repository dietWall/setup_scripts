#! /usr/bin/env python3

import os

default_key_path = ""

if os.name == 'nt':
    default_key_path = os.path.join(os.environ['USERPROFILE'], '.ssh')
else:
    default_key_path = os.path.join(os.environ['HOME'], '.ssh' )

def get_filename(key_path: str, key_type : str) -> str:
    filename = os.path.join(key_path, f'id_{key_type}')    
    if os.path.exists(filename) == True:
        suffix = 1

        while os.path.exists(filename) == True:
            filename = os.path.join(key_path, f'id_{key_type}_{suffix}')
            suffix += 1
    return filename


def generate_ssh_key(key_path: str, key_type: str = 'rsa') -> int:
    """Generate an SSH key of the specified type and save it to the given path.
    Args:
        key_type (str): The type of SSH key to generate ('rsa', 'dsa', 'ecdsa', 'ed25519').
        key_path (str): The directory where the generated key will be saved.
    """
    if not key_type:
        print("No key type specified. Please use --generate with a valid key type.")
        return 1
    if not os.path.isdir(key_path):
        print(f"Directory does not exist: {key_path}")
        return 1
    filename = get_filename(key_path, key_type)

    print(f"generating {key_type} key at {filename}")

    import subprocess
    try:
        result = subprocess.run(
            ["ssh-keygen", "-t", key_type, "-f", filename, "-N", ""],
            capture_output=True
        )
    except FileNotFoundError:
        print("ssh-keygen not found. Please install openssh-client or ensure ssh-keygen is in PATH.")
        return 1
    print(f"ssh-keygen exited with return code {result.returncode}, output:")
    
    for l in result.stdout.decode().splitlines():
        print(f"stdout: {l}")

    return result.returncode

def get_key_type_from_path(key_path: str) -> str | None:
    """Detect key type from existing SSH key files in the given directory."""
    for key_type in ["rsa", "dsa", "ecdsa", "ed25519"]:
        pub_file = os.path.join(key_path, f"id_{key_type}.pub")
        if os.path.exists(pub_file):
            return key_type
    return None


def deploy(file: str, user_at_host: str, password: str) -> int:
    # paramiko.connect requires an explicit username, so we enforce user@host format
    if '@' not in user_at_host:
        print(f"Invalid host format: {user_at_host}. Expected <user>@<host>. Use --deploy-to-host user@host.")
        return 1
    user = user_at_host.split('@')[0]
    server = user_at_host.split('@')[1]
    with open(file, 'r') as f:
        key = f.read()

    import paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=user, password=password)
    channel = client.exec_command('mkdir -p ~/.ssh/ && cat >> ~/.ssh/authorized_keys')
    channel.stdin.write(key.encode())
    channel.stdin.flush()
    channel.stdin.close()
    channel.recv_exit_status()
    client.exec_command('chmod 644 ~/.ssh/authorized_keys && chmod 700 ~/.ssh/')
    return 0

def add_to_ssh_config(host: str, user: str, key_path: str, key_type: str, config_path: str = None) -> str:
    """Add a Host entry to ~/.ssh/config for localhost with the generated key."""
    if config_path is None:
        config_path = os.path.join(default_key_path, "config")
    host_entry = f"""Host {host}
    HostName localhost
    User {user}
    IdentityFile {os.path.join(key_path, f"id_{key_type}")}
"""

    if os.path.exists(config_path):
        with open(config_path, 'a') as f:
            f.write(f"\n{host_entry}")
    else:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            f.write(host_entry)

    print(f"Added {host} to {config_path}")
    return config_path

def test_ssh_config(host: str, config_path: str = None) -> int:
    """Validate SSH config for the given host using ssh -G."""
    import subprocess
    cmd = ["ssh", "-G"]
    if config_path:
        cmd.extend(["-F", config_path])
    cmd.append(host)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SSH config validation failed for {host}: {result.stderr.strip()}")
        return result.returncode
    print(f"SSH config valid for {host}")
    return 0

def password_prompt() -> str:
    import getpass
    password = getpass.getpass(prompt="Enter password for deployment: ")
    return password

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Manage and deploy SSH keys.")

    parser.add_argument(
        "--generate", choices=["rsa", "dsa", "ecdsa", "ed25519"],
        help="Generate a new SSH key of the specified type.", default=None)
    parser.add_argument(
        "--key-path", type=str,
        help="Path to the file for generated key", default=default_key_path)
    # paramiko.connect requires an explicit username, so we enforce user@host format
    parser.add_argument("--deploy-to-host", type=str, help="deploys the key from --key-path to the given <user>@<host> via ssh", default=None)
    parser.add_argument("--add-to-config", action="store_true", help="adds a Host entry to ~/.ssh/config pointing to localhost", default=False)
    parser.add_argument("--password_type", type=str, help="password input type", choices=["prompt", "dotenv"], default="prompt")
    parser.add_argument("--dotenv-file", type=str, help="defines the .env file location", default="/home/appuser/code/.env")
    
    args = parser.parse_args()
    print(f"args: {args}")

    if args.generate is not None:
        print(f"Generating {args.generate} SSH key at {args.key_path}...")

        if generate_ssh_key(args.key_path, args.generate) != 0:
            print("Failed to generate SSH key.")
        else:
            print(f"SSH key with {args.generate} generated at {args.key_path}")

    if args.deploy_to_host is not None:
        key_type = args.generate if args.generate is not None else get_key_type_from_path(args.key_path)
        if key_type is None:
            print("No key type specified. Use --generate or ensure an existing key is in --key-path.")
            exit(1)

        print(f"Deploying {key_type} key to {args.deploy_to_host}...")
        public_key_path = os.path.join(args.key_path, f'id_{key_type}.pub')

        if not os.path.exists(public_key_path):
            print(f"Public key not found at {public_key_path}. Cannot deploy.")
        else:
            password = ""
            if args.password_type == "prompt":
                password = password_prompt()
            else:
                from dotenv import dotenv_values
                config = dotenv_values(args.dotenv_file)
                password = config.get("PASSWORD", "")

            if password is not None and password != "":
                result = deploy(public_key_path, args.deploy_to_host, password)

                if result != 0:
                    print("Failed to deploy SSH key.")
                else:
                    print(f"SSH key {public_key_path} deployed to {args.deploy_to_host} successfully.")
            else:
                print("No password provided. Cannot deploy.")
                exit(1)

    if args.add_to_config:
        if args.deploy_to_host is None:
            print("--add-to-config requires --deploy-to-host to specify the host.")
            exit(1)
        key_type = args.generate if args.generate is not None else get_key_type_from_path(args.key_path)
        if key_type is None:
            print("No key type specified. Use --generate or ensure an existing key is in --key-path.")
            exit(1)
        user = args.deploy_to_host.split('@')[0]
        host = args.deploy_to_host.split('@')[1]
        config_path = add_to_ssh_config(host, user, args.key_path, key_type)
        test_ssh_config(host, config_path)

    exit(0)

if __name__ == "__main__":
    main()