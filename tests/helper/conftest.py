
import pytest
#we cannot do the test setup with the package that we want to test
#so supbrocess here instead of repo_helper
import subprocess

######################################
# repo_helper
######################################

@pytest.fixture(scope="session")
def repo_root():
    command = "git rev-parse --show-toplevel"
    output = subprocess.run(command, shell=True, capture_output=True)
    print(output.stdout)
    return output.stdout.decode("utf-8").strip()

@pytest.fixture(scope="session", autouse=True)
def build_repo_helper(repo_root):
    cmd = "python3 -m build ."
    subprocess.run(args=cmd, shell=True, cwd=repo_root)

@pytest.fixture(scope="session", autouse=True)
def repo_helper(repo_root, build_repo_helper):
    cmd = "pip install ."
    subprocess.run(args=cmd, shell=True, cwd=repo_root)


@pytest.fixture(scope="function")
def cleanup(container_name: str):
    #this takes all container names, that has been started during a test
    # and stops it afterwards, otherwise the test will fail in the next run
    print(f"started container: {container_name}")
    containers_to_stop = []
    containers_to_stop.append(container_name)
    yield
    for c in containers_to_stop:
        subprocess.run(f"docker stop {c}", shell=True)
        subprocess.run(f"docker rm {c}", shell=True)

