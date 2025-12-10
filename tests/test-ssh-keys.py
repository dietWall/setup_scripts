
#generate each key once
#deploy each key to a second container

import pytest


@pytest.mark.parametrize("key_type", ["rsa", "dsa", "ecdsa", "ed25519"])
def test_ssh_keys_generation(client_container, key_type):
    print("") #newline 

    key_path = f"/home/appuser/keys/"
    exec_result = client_container.exec_run(cmd=f"/home/appuser/ssh-keys.py --generate {key_type} --key-path={key_path}", demux=True)
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
            
        
    
