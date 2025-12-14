import pytest

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