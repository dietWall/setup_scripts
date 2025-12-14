
#generate each key once
#deploy each key to a second container

import pytest

def test_show_code_directory(client_container):
    print("") #newline 

    cmd = "ls -la /home/appuser"
    exec_result = client_container.exec_run(cmd=cmd, demux=True)
    print(f"exit code: {exec_result.exit_code}")
    for line in exec_result.output[0].decode('utf-8').splitlines():
        print(f"{line}")

    cmd = "ls -la /home/appuser/code/ssh/"
    exec_result = client_container.exec_run(cmd=cmd, demux=True)
    print(f"exit code: {exec_result.exit_code}")
    for line in exec_result.output[0].decode('utf-8').splitlines():
        print(f"{line}")

@pytest.mark.parametrize("key_type", ["rsa", "dsa", "ecdsa", "ed25519"])
def test_ssh_keys_generation(client_container, key_type):
    print("") #newline 

    key_path = f"/home/appuser/keys/"
    cmd=f"/home/appuser/code/ssh/ssh-keys.py --generate {key_type} --key-path={key_path}"
    
    print(f"running:")
    print(f"{cmd}")

    exec_result = client_container.exec_run(cmd=cmd, demux=True)
    print(f"exit code: {exec_result.exit_code}")
    
    for line in exec_result.output[0].decode('utf-8').splitlines():
        print(f"{line}")

    assert exec_result.exit_code == 0, f"Key generation failed for {key_type}"

    print(f"testing for existence of key file at {key_path}id_{key_type}.pub")
    exec_result = client_container.exec_run(cmd=f"ls -la {key_path}", demux=True)
    print(f"File exists: {exec_result.exit_code}")
    
    if exec_result.output[0] is not None:
        for line in exec_result.output[0].decode('utf-8').splitlines():
            print(f"{line}")

@pytest.mark.parametrize("key_type", ["rsa", "dsa", "ecdsa", "ed25519"])
def test_ssh_keys_deploy(client_container, server_container, key_type):
    print("") #newline 

    print(f"testing deployment of {key_type} key to {server_container.name}")
    
    cmd=f'''/bin/bash -c \"source /home/appuser/ssh-venv/bin/activate && /home/appuser/code/ssh/ssh-keys.py --generate {key_type} --deploy appuser@ssh-server --password_type dotenv\"'''

    print(f"running:")
    print(f"{cmd}")

    exec_result = client_container.exec_run(cmd=cmd, demux=True)
    print(f"exit code: {exec_result.exit_code}")
    
    for line in exec_result.output[0].decode('utf-8').splitlines():
        print(f"{line}")

    assert exec_result.exit_code == 0, "Key deployment failed"
    # it would be good to test the connection without password, which is actually the final goal
    # but that requires more setup