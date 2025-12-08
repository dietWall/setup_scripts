#! python3


import os

default_key_path = ""

if os.name == 'nt':
    default_key_path = os.path.join(os.environ['USERPROFILE'], '.ssh')
else:
    default_key_path = os.path.join(os.environ['HOME'], '.ssh' )


def generate_ssh_key(key_path: str, key_type: str = 'rsa') -> int:
    """Generate an SSH key of the specified type and save it to the given path.
    Args:
        key_type (str): The type of SSH key to generate ('rsa', 'dsa', 'ecdsa', 'ed25519').
        key_path (str): The directory where the generated key will be saved.
    """
    filename = os.path.join(key_path, f'id_{key_type}')

    import subprocess
    result = subprocess.run(
        ["ssh-keygen", "-t", key_type, "-f", filename, "-N", ""],
        capture_output=True
    )
    print(f"ssh-keygen exited with return code {result.returncode}, output:")
    
    for l in result.stdout.decode().splitlines():
        print(f"stdout: {l}")

    return result.returncode

def deploy_ssh_key_to_host(file: str, user_at_host: str) -> int:
    """Deploy the SSH public key to the specified user@host 
    on Linux: using ssh-copy-id
    on Windows: a specific ssh command on windows.
    Args:
        file (str): Public key file to deploy.
        user_at_host (str): The target in the format user@host where the key will be deployed.
    """
    commmand = ""
    
    if os.name == 'nt':
        commmand = f'type {file} | ssh {user_at_host} "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"'
    elif os.name == 'posix':
        commmand = f'ssh-copy-id -i {file} {user_at_host}'
    else:
        raise NotImplementedError("Unknown OS, not implemented.")

    import subprocess
    result = subprocess.run(
        commmand,
        capture_output=True
    )

    print(f"copying resulted in {result.returncode}, output:")
    
    for l in result.stdout.decode().splitlines():
        print(f"stdout: {l}")

    return result.returncode


def find_key_file(key_path: str, key_type: str = 'rsa') -> str:
    """Find the SSH key file of the specified type in the given path.
    Args:
        key_type (str): The type of SSH key ('rsa', 'dsa', 'ecdsa', 'ed25519').
        key_path (str): The directory path where the key files are stored.
    Returns:
        str: The full path to the SSH key file if found, else an empty string.
    """
    return ""
    # if key_type is "rsa":
    #     filename = os.path.join(key_path, f'id_{key_type}')
    # else if key_type is "dsa":
    #     filename = os.path.join(key_path, f'id_{key_type}')
    # else if key_type is "ecdsa":
    #     filename = os.path.join(key_path, f'id_{key_type}')
    # else if key_type is "ed25519":
    #     filename = os.path.join(key_path, f'id_{key_type}')
    
    # if os.path.exists(filename):
    #     return filename
    # else:
    #     return ""

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
            import subprocess
            result = subprocess.run(
                ["ssh-copy-id", "-i", public_key_path, args.deploy_to_host],
                capture_output=True
            )
            print(f"ssh-copy-id exited with return code {result.returncode}, output:")
            for l in result.stdout.decode().splitlines():
                print(f"stdout: {l}")
            if result.returncode != 0:
                print("Failed to deploy SSH key.")
            else:
                print(f"SSH key deployed to {args.deploy_to_host} successfully.")

    import sys
    sys.exit(0)