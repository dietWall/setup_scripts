import pytest

from repo_helpers.Repo_Helper import Repo_Helper

@pytest.fixture(scope="package")
def env_file():
    helper = Repo_Helper()
    env_path = f"{helper.repo_root()}test_log/.env"
    helper.execute("mkdir -p test_log")
    helper.execute(f"touch {env_path}")
    return env_path


@pytest.fixture(scope="package")
def image():
    image_name = "ssh-image"
    helper = Repo_Helper(logfile="test_log/image_build.txt")
    print(f"building image")
    result = helper.build_docker_image(f"{helper.repo_root()}/ssh/", image_name=image_name)
    if result != 0:
        print(f"image build failed with {result}")
    return image_name

@pytest.fixture(scope="package")
def network(env_file, image):
    helper = Repo_Helper(logfile="test_log/compose.txt")
    print(f"starting ssh_network")
    result = helper.compose_up(f"{helper.repo_root()}/tests/data/compose.yml")
    if result.returncode != 0:
        raise RuntimeError(f"docker-compose result: {result.returncode}")
    yield
    print(f"stopping ssh-network")
    result, output = helper.execute(f"docker compose -f {helper.repo_root()}/tests/data/compose.yml down")
    if result.returncode != 0:
        print(f"docker-compose down failed with: {result.returncode}")
        for l in output:
            print(l)

@pytest.fixture(scope="function")
def client(network):
    helper = Repo_Helper()
    containers = helper.get_containers(image="ssh-image")
    for con in containers:
        if con.names == 'ssh-client':
            return con
    raise RuntimeError("ssh-client container not found in test setup.")

@pytest.fixture(scope="function")
def server(network):
    helper = Repo_Helper()
    containers = helper.get_containers(image="ssh-image")
    for con in containers:
        if con.names == 'ssh-server':
            return con
    raise RuntimeError("ssh-server container not found in test setup.")


@pytest.fixture(scope="session", autouse=True)
def log_dir():
    dir = "test_log"
    helper = Repo_Helper()
    command = f"mkdir -p {helper.repo_root()}/{dir}"
    helper.execute(command)
    return dir





    