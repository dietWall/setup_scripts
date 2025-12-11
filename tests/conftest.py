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
        for line in compose_result.stdout.decode('utf-8').splitlines():
            print(f"{line}")
        for line in compose_result.stderr.decode('utf-8').splitlines():
            print(f"{line}")
        raise RuntimeError(f"docker-compose returned: {compose_result.returncode}")
    
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