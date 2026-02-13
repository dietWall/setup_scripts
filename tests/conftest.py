import pytest
import subprocess

def create_empty_env_file(repo_root):
    env_path = f"{repo_root}/.env"
    import os
    if os.path.exists(f"{repo_root}/.env") == False:
        with open(env_path, "w") as f:
            f.write("\n")
    return env_path

def run_network(repo_root):
    create_empty_env_file(repo_root)

    import subprocess
    compose_result = subprocess.run(
        ["docker", "compose", "-f", f"{repo_root}/tests/compose.yml", "up", "-d"],
        capture_output=True
    )
    if compose_result.returncode != 0:
        for line in compose_result.stdout.decode('utf-8').splitlines():
            print(f"{line}")
        for line in compose_result.stderr.decode('utf-8').splitlines():
            print(f"{line}")
        raise RuntimeError(f"docker-compose returned: {compose_result.returncode}")

def client(containers):
    for con in containers:
        if con.name == 'ssh-client':
            return con
    raise RuntimeError("ssh-client container not found in test setup.")

def server(containers):
    for con in containers:
        if con.name == 'ssh-server':
            return con
    raise RuntimeError("ssh-server container not found in test setup.")

def network():
    import docker
    client = docker.from_env()
    containers = client.containers.list(filters={"ancestor": "ssh-image"})
    return containers

@pytest.fixture(scope="session", autouse=True)
def repo_root() -> str:
    import subprocess    
    git_result = subprocess.run(["git", "rev-parse", "--show-toplevel"],capture_output=True)
    repo_root = git_result.stdout.strip().decode("utf-8")
    return repo_root

@pytest.fixture(scope="session", autouse=True)
def containers(repo_root):
    run_network(repo_root)
    containers = network()
    yield containers
    
    for con in containers:
        con.stop()
        con.remove()

@pytest.fixture(scope="session", autouse=True)
def client_container(containers):
    return client(containers)

@pytest.fixture(scope="session", autouse=True)
def server_container(containers):
    return server(containers)


@pytest.fixture(scope="session", autouse=True)
def log_dir():
    dir = "test_log"
    command = f"mkdir -p {dir}"
    result = subprocess.run(command, shell=True)
    return dir

@pytest.fixture(scope="session", autouse=True)
def build_repo_helper(repo_root):
    cmd = "python3 -m build ."
    subprocess.run(args=cmd, shell=True, cwd=repo_root)

@pytest.fixture(scope="session", autouse=True)
def repo_helper(repo_root, build_repo_helper):
    cmd = "pip install ."
    subprocess.run(args=cmd, shell=True, cwd=repo_root)

containers_to_stop = []

@pytest.fixture(scope="function")
def cleanup(container_name: str):
    #this takes all container names, that has been started during a test
    # and stops it afterwards, otherwise the test will fail in the next run
    print(f"started container: {container_name}")
    containers_to_stop.append(container_name)
    yield
    for c in containers_to_stop:
        subprocess.run(f"docker stop {c}", shell=True)
        subprocess.run(f"docker rm {c}", shell=True)




    