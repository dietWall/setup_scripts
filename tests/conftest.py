import pytest

@pytest.fixture(scope="session", autouse=True)
def repo_root() -> str:
    import subprocess    
    git_result = subprocess.run(["git", "rev-parse", "--show-toplevel"],capture_output=True)
    repo_root = git_result.stdout.strip().decode("utf-8")
    return repo_root

@pytest.fixture(scope="session", autouse=True)
def containers(repo_root):
    import subprocess
    compose_result = subprocess.run(
        ["docker", "compose", "-f", f"{repo_root}/tests/compose.yml", "up", "-d"],
        capture_output=True
    )
    if compose_result.returncode != 0:
        raise RuntimeError("Failed to start docker-compose services for tests.")
    
    import docker
    client = docker.from_env()
    containers = client.containers.list(filters={"ancestor": "ssh-image"})

    yield containers
    
    for con in containers:
        con.stop()
        con.remove()

@pytest.fixture(scope="session", autouse=True)
def client_container(containers):
    for con in containers:
        if con.name == 'ssh-client':
            return con
    raise RuntimeError("ssh-client container not found in test setup.")

@pytest.fixture(scope="session", autouse=True)
def server_container(containers):
    for con in containers:
        if con.name == 'ssh-server':
            return con
    raise RuntimeError("ssh-server container not found in test setup.")