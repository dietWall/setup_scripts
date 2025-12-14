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
    filename = get_filename(key_path, key_type)

    print(f"generating {key_type} key at {filename}")

    import subprocess
    result = subprocess.run(
        ["ssh-keygen", "-t", key_type, "-f", filename, "-N", ""],
        capture_output=True
    )
    print(f"ssh-keygen exited with return code {result.returncode}, output:")
    
    for l in result.stdout.decode().splitlines():
        print(f"stdout: {l}")

    return result.returncode

def deploy(file: str, user_at_host: str, password: str) -> int:
    user = user_at_host.split('@')[0]
    server = user_at_host.split('@')[1]
    with open(file, 'r') as f:
        key = f.read()

    import paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=user, password=password)
    client.exec_command('mkdir -p ~/.ssh/')
    client.exec_command('echo "%s" > ~/.ssh/authorized_keys' % key)
    client.exec_command('chmod 644 ~/.ssh/authorized_keys')
    client.exec_command('chmod 700 ~/.ssh/')
    return 0

def password_prompt() -> str:
    import getpass
    password = getpass.getpass(prompt="Enter password for deployment: ")
    return password

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manage and deploy SSH keys.")

    parser.add_argument(
        "--generate", choices=["rsa", "dsa", "ecdsa", "ed25519"],
        help="Generate a new SSH key of the specified type.", default=None)
    parser.add_argument(
        "--key-path", type=str,
        help="Path to the file for generated key", default=default_key_path)
    parser.add_argument("--deploy-to-host", type=str, help="deploys the key from --key-path to the given <user>@<host> via ssh", default=None)
    #we need dotenv option for tests
    parser.add_argument("--password_type", type=str, help="password input type", choices=["prompt", "dotenv"], default="prompt")
    parser.add_argument("--dotenv-file", type=str, help="defines the .env file location", default="/home/appuser/code/.env")
    
    args = parser.parse_args()
    print(f"args: {args}")

    if args.generate != None:
        print(f"Generating {args.generate} SSH key at {args.key_path}...")

        if generate_ssh_key(args.key_path, args.generate) != 0:
            print("Failed to generate SSH key.")
        else:
            print(f"SSH key with {args.generate} generated at {args.key_path}")

    if args.deploy_to_host != None:
        print(f"Deploying SSH key to {args.deploy_to_host}...")
        public_key_path = os.path.join(args.key_path, f'id_{args.generate}.pub')
        
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
    exit(0)